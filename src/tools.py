
# Generate a answer implementing the recuperation content
def generate(state: MessagesState):
    """Generate answer."""
    # Obtain the tools messages (retrieved content)
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    if not tool_messages:
        docs_content = "No se encontró información relevante."
    else:
        docs_content = "\n\n".join(set(doc.content for doc in tool_messages))

    # Create the system message with the recuperation context
    system_message_content = (
        "Usted es un asistente para tareas de respuesta a preguntas. "
        "Utilice los siguientes elementos de contexto recuperados para responder "
        "las preguntas. Si no conoces la respuesta, di que no la sabes. "
        "Utiliza cinco frases como máximo para responder concisamente."
        "\n\n"
        f"{docs_content}"
    )

    # Obtain the conversation messages (history)
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]

    # Create the prompt with the history and the context
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Generate the answer with the language model
    response = llm.invoke(prompt)

    # Add the answer to history
    message_history.add_ai_message(response.content)

    # Return the update state
    return {"messages": [response]}

# Graph Configuration
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

# Graph Compilation
graph = graph_builder.compile()

# Execute the graph with the input message
input_message = "Quiero que me digas los tipos de conjunciones?"

for step in graph.stream(
    {"messages": [HumanMessage(content=input_message)]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()

# Show the message history
print("\nHistorial de mensajes:")
for message in message_history.messages:
    print(f"{message.type}: {message.content}")