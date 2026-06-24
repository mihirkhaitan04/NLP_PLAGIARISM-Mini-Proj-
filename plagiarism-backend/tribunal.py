import os
from typing import TypedDict, List
from dotenv import load_dotenv

# LangChain & LangGraph imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

load_dotenv()

# Define the State of our Graph
class TribunalState(TypedDict):
    document_text: str
    historical_texts: List[str]
    prosecutor_arg: str
    defense_arg: str
    final_score: int
    final_verdict: str

# 1. Prosecutor Node
def prosecutor_node(state: TribunalState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Prosecutor in a Forensic Stylometry Tribunal. Your job is to prove that the 'New Document' was NOT written by the same author as the 'Historical Documents' (i.e. it was plagiarized or AI generated). Analyze the vocabulary, sentence length, tone, and punctuation. Write a 1-paragraph aggressive argument pointing out stylistic differences."),
        ("user", "Historical Documents (Baseline Fingerprint):\n{history}\n\nNew Document:\n{new_doc}")
    ])
    
    chain = prompt | llm
    history_str = "\n---\n".join(state["historical_texts"][:3])
    
    response = chain.invoke({
        "history": history_str,
        "new_doc": state["document_text"]
    })
    
    state["prosecutor_arg"] = response.content
    return state

# 2. Defense Node
def defense_node(state: TribunalState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Defense Attorney in a Forensic Stylometry Tribunal. The Prosecutor just argued that the New Document was plagiarized or AI generated due to stylistic differences. Your job is to defend the author. Read the Prosecutor's argument, then write a 1-paragraph defense pointing out stylistic similarities to the historical documents, or arguing why the differences are just natural variations in academic writing."),
        ("user", "Historical Documents:\n{history}\n\nNew Document:\n{new_doc}\n\nProsecutor's Argument:\n{prosecutor_arg}")
    ])
    
    chain = prompt | llm
    history_str = "\n---\n".join(state["historical_texts"][:3])
    
    response = chain.invoke({
        "history": history_str,
        "new_doc": state["document_text"],
        "prosecutor_arg": state["prosecutor_arg"]
    })
    
    state["defense_arg"] = response.content
    return state

# 3. Judge Node
def judge_node(state: TribunalState):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Judge in a Forensic Stylometry Tribunal. You will read the Prosecutor's attack and the Defense's counter-argument. You must decide if the 'New Document' matches the author's historical writing style. \n\nYou MUST return your answer in EXACTLY the following format:\nSCORE: <a number from 0 to 100, where 100 means perfect match (innocent) and 0 means definitely a different author (guilty)>\nVERDICT: <a 1-paragraph final ruling explaining which argument was stronger and your final conclusion>"),
        ("user", "Prosecutor's Argument:\n{prosecutor_arg}\n\nDefense's Argument:\n{defense_arg}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "prosecutor_arg": state["prosecutor_arg"],
        "defense_arg": state["defense_arg"]
    })
    
    content = response.content
    
    # Parse the SCORE and VERDICT safely
    try:
        lines = content.split('\n')
        score_line = [l for l in lines if l.startswith("SCORE:")][0]
        verdict_line = [l for l in lines if l.startswith("VERDICT:")][0]
        
        score_str = score_line.replace("SCORE:", "").strip().replace('%', '')
        state["final_score"] = int(score_str)
        state["final_verdict"] = verdict_line.replace("VERDICT:", "").strip()
    except Exception as e:
        state["final_score"] = 50
        state["final_verdict"] = f"Error parsing judge verdict: {content}"
        
    return state

# Compile the LangGraph
workflow = StateGraph(TribunalState)
workflow.add_node("prosecutor", prosecutor_node)
workflow.add_node("defense", defense_node)
workflow.add_node("judge", judge_node)

# Flow: Prosecutor -> Defense -> Judge
workflow.add_edge(START, "prosecutor")
workflow.add_edge("prosecutor", "defense")
workflow.add_edge("defense", "judge")
workflow.add_edge("judge", END)

app = workflow.compile()

def run_tribunal(new_text: str, historical_texts: List[str]) -> dict:
    """Executes the LangGraph Multi-Agent Debate."""
    # If no history, we can't do stylometry
    if not historical_texts or len(historical_texts) == 0:
        return {
            "prosecutor": "N/A - No historical documents found for this user to build a fingerprint.",
            "defense": "N/A - Insufficient data.",
            "score": 100,
            "verdict": "Author match assumed (Insufficient historical data to prove otherwise)."
        }
        
    initial_state = TribunalState(
        document_text=new_text,
        historical_texts=historical_texts,
        prosecutor_arg="",
        defense_arg="",
        final_score=0,
        final_verdict=""
    )
    
    result_state = app.invoke(initial_state)
    
    return {
        "prosecutor": result_state.get("prosecutor_arg", ""),
        "defense": result_state.get("defense_arg", ""),
        "score": result_state.get("final_score", 0),
        "verdict": result_state.get("final_verdict", "")
    }

if __name__ == "__main__":
    # Test script
    hist = ["The quick brown fox jumps over the lazy dog.", "A completely different sentence written by me."]
    new_doc = "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve problems too complex for classical computers."
    res = run_tribunal(new_doc, hist)
    print("PROSECUTOR:", res["prosecutor"])
    print("DEFENSE:", res["defense"])
    print("SCORE:", res["score"])
    print("VERDICT:", res["verdict"])
