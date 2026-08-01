# LangGraph StateGraph definition: Detector → Investigator → Hypothesis-Ranker → Narrator → Critic.
# Each node is an HTTP call to the corresponding agent FastAPI service (not in-process logic).
# State carries anomaly_id and intermediate artifacts; write AgentTrace documents at every hop.
