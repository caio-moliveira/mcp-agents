import streamlit as st
from fastmcp import Client
import asyncio
import json
from datetime import date
import re

st.set_page_config(page_title="AI Travel Planner", page_icon="🌍", layout="centered")

st.title("🌍 AI Travel Planner")
st.markdown("""
Plan your trip with AI-powered agents that find:
- ✈️ Flights
- 🏠 Stays
- 📍 Local attractions and experiences

Just tell us when and where you're going!
""")

# Input Form
with st.form("travel_form"):
    departure = st.text_input("Departure City", placeholder="e.g. Lisbon")
    destination = st.text_input("Destination City", placeholder="e.g. Berlin")
    start_date = st.date_input("Start Date", min_value=date.today())
    end_date = st.date_input("End Date", min_value=start_date)
    num_travelers = st.number_input("Number of Travelers", min_value=1, step=1, value=1)
    attractions = st.multiselect(
        "What are you interested in?",
        ["cultural", "local food", "parks", "pubs"],
        default=["cultural"],
    )
    accommodation_type = st.selectbox(
        "Accommodation Type", options=["hotel", "apartment", "hostel"]
    )
    submitted = st.form_submit_button("Plan My Trip")


# Helper to call MCP server
async def call_planner(payload):
    client = Client("http://localhost:8003/sse")
    async with client:
        result = await client.call_tool("travel_planner", {"input_data": payload})
        return result[0].text if result and hasattr(result[0], "text") else str(result)


# Parser for Airbnb output
def parse_airbnb_markdown(raw_block: str):
    parsed = {}
    for line in raw_block.strip().split("\n"):
        if ": " in line:
            key, val = line.split(": ", 1)
            key = key.strip(" -*").lower().replace(" ", "_")
            parsed[key] = val.strip()
    return parsed


# Handle Submission
if submitted:
    if not departure or not destination:
        st.warning("Please enter both departure and destination cities.")
    else:
        payload = {
            "departure": departure,
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "num_travelers": num_travelers,
            "attractions": attractions,
            "accommodation_type": accommodation_type,
        }

        st.info("🧠 Agents are planning your trip...")

        try:
            output = asyncio.run(call_planner(payload))

            try:
                data = json.loads(output)
                st.subheader("🧳 Trip Plan Breakdown")

                if "tasks_output" in data:
                    for task in data["tasks_output"]:
                        agent = task.get("agent", "Agent")
                        st.markdown(f"### 🤖 {agent}")

                        if "Flight" in agent:
                            st.markdown("#### ✈️ Flight Options")
                            st.markdown(task["raw"])

                        elif "Airbnb" in agent:
                            st.markdown("#### 🏠 Recommended Accommodations")
                            listings = task["raw"].split("\n\n")
                            for i, block in enumerate(listings):
                                if block.strip():
                                    item = parse_airbnb_markdown(block)
                                    cols = st.columns([3, 1])
                                    with cols[0]:
                                        st.markdown(
                                            f"**{item.get('listing_name', f'Accommodation {i + 1}')}**"
                                        )
                                        st.markdown(
                                            f"💵 **{item.get('total_price', 'N/A')}** ({item.get('price_per_night', 'N/A')})"
                                        )
                                        st.markdown(f"⭐ {item.get('rating', 'N/A')}")
                                        if "key_features" in item:
                                            st.markdown(f"🔑 {item['key_features']}")
                                    with cols[1]:
                                        if "direct_booking_link" in item:
                                            st.link_button(
                                                "🔗 Book Now",
                                                item["direct_booking_link"],
                                            )

                        elif "Experience" in agent or "Brave Search" in agent:
                            st.markdown("#### 📍 Top Local Experiences")
                            for entry in task["raw"].split("\n\n"):
                                if entry.strip():
                                    st.markdown(f"- {entry}")

                        else:
                            st.code(task["raw"])

                elif "raw" in data:
                    st.markdown("### 📄 Raw Output")
                    st.write(data["raw"])

            except Exception:
                st.error("⚠️ Failed to parse the agent output.")
                st.text(output)

        except Exception as e:
            st.error(f"Error: {str(e)}")
