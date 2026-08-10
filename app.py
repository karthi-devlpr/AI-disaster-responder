import streamlit as st
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import uuid


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Emergency Response Platform",
    page_icon="🚨",
    layout="wide"
)


# ============================================================
# DEMO DATA
# ============================================================

if "incidents" not in st.session_state:
    st.session_state.incidents = [
        {
            "id": "INC-1001",
            "type": "Flood",
            "description": "Flood water entering residential area.",
            "lat": 15.5057,
            "lon": 80.0499,
            "area": "Ongole",
            "severity": "High",
            "status": "Reported",
            "created": "2026-08-10 09:30",
            "responder": None,
            "ai": "Possible flood; suggested severity: High",
            "image_name": None
        }
    ]


if "responders" not in st.session_state:
    st.session_state.responders = [
        {
            "name": "Ongole Rescue Team",
            "lat": 15.5050,
            "lon": 80.0505,
            "available": True,
            "capability": ["Flood", "Rescue"]
        },
        {
            "name": "Ongole Fire Team",
            "lat": 15.5100,
            "lon": 80.0450,
            "available": True,
            "capability": ["Fire", "Rescue", "Flood"]
        },
        {
            "name": "Nearby District Team",
            "lat": 15.9000,
            "lon": 80.1000,
            "available": True,
            "capability": ["Flood", "Rescue"]
        }
    ]


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def distance_km(lat1, lon1, lat2, lon2):

    earth_radius = 6371.0

    lat1 = radians(lat1)
    lat2 = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


# ============================================================
# FIND NEARBY RESPONDERS
# ============================================================

def find_nearby_responders(incident):

    eligible = []

    for responder in st.session_state.responders:

        if not responder["available"]:
            continue

        if incident["type"] not in responder["capability"]:
            continue

        distance = distance_km(
            incident["lat"],
            incident["lon"],
            responder["lat"],
            responder["lon"]
        )

        eligible.append(
            (
                distance,
                responder["name"]
            )
        )

    return sorted(eligible)


# ============================================================
# CREATE INCIDENT
# ============================================================

def create_incident(
    incident_type,
    description,
    latitude,
    longitude,
    image_name
):

    incident_id = (
        "INC-"
        + str(uuid.uuid4())[:8].upper()
    )

    if incident_type in [
        "Flood",
        "Fire",
        "Medical",
        "Accident"
    ]:
        severity = "High"
    else:
        severity = "Medium"

    incident = {

        "id": incident_id,

        "type": incident_type,

        "description": description,

        "lat": latitude,

        "lon": longitude,

        "area": "Ongole / detected area",

        "severity": severity,

        "status": "Reported",

        "created": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),

        "responder": None,

        "ai": (
            f"AI demo analysis: possible "
            f"{incident_type.lower()}; "
            f"suggested severity: {severity}."
        ),

        "image_name": image_name
    }

    st.session_state.incidents.insert(
        0,
        incident
    )

    return incident_id


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🚨 Emergency Platform"
)

portal = st.sidebar.radio(
    "Select Portal",
    [
        "Citizen Portal",
        "Admin Dashboard",
        "Responder Dashboard"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "AI Emergency Response Platform"
)


# ============================================================
# CITIZEN PORTAL
# ============================================================

if portal == "Citizen Portal":

    st.title(
        "👤 Citizen Portal"
    )

    st.write(
        "Report an emergency with "
        "location, description and "
        "optional image."
    )

    st.divider()

    with st.form("incident_form"):

        st.subheader(
            "🚨 Report Emergency"
        )

        incident_type = st.selectbox(
            "Emergency Type",
            [
                "Flood",
                "Fire",
                "Accident",
                "Medical",
                "Crime / Safety",
                "Other"
            ]
        )

        description = st.text_area(
            "Describe what happened",
            placeholder=(
                "Example: Flood water has "
                "entered houses and people "
                "need assistance."
            )
        )

        st.subheader(
            "📍 Incident Location"
        )

        col1, col2 = st.columns(2)

        with col1:
            latitude = st.number_input(
                "Latitude",
                value=15.5057,
                format="%.6f"
            )

        with col2:
            longitude = st.number_input(
                "Longitude",
                value=80.0499,
                format="%.6f"
            )

        image = st.file_uploader(
            "📷 Upload Incident Image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )

        submitted = st.form_submit_button(
            "🚨 Submit Emergency Report"
        )

    if submitted:

        if not description.strip():

            st.error(
                "Please describe the emergency."
            )

        else:

            incident_id = create_incident(
                incident_type,
                description,
                latitude,
                longitude,
                image.name
                if image
                else None
            )

            st.success(
                f"Emergency report submitted! "
                f"Incident ID: {incident_id}"
            )

    st.divider()

    st.subheader(
        "📋 Recent Reports"
    )

    for incident in (
        st.session_state.incidents[:5]
    ):

        st.write(
            f"**{incident['id']}** · "
            f"{incident['type']} · "
            f"{incident['area']} · "
            f"Status: **{incident['status']}**"
        )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

elif portal == "Admin Dashboard":

    st.title(
        "🏢 Admin Dashboard"
    )

    st.write(
        "Manage incidents within the "
        "administrator's authorized area."
    )

    incidents = (
        st.session_state.incidents
    )

    total = len(incidents)

    high_priority = sum(
        incident["severity"] == "High"
        for incident in incidents
    )

    active = sum(
        incident["status"] != "Resolved"
        for incident in incidents
    )

    assigned = sum(
        incident["responder"] is not None
        for incident in incidents
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Incidents",
        total
    )

    col2.metric(
        "High Priority",
        high_priority
    )

    col3.metric(
        "Active",
        active
    )

    col4.metric(
        "Assigned",
        assigned
    )

    st.divider()

    for incident in incidents:

        icon = (
            "🔴"
            if incident["severity"] == "High"
            else "🟡"
        )

        with st.expander(
            f"{icon} "
            f"{incident['id']} — "
            f"{incident['type']} — "
            f"{incident['status']}"
        ):

            st.write(
                "**Description:**",
                incident["description"]
            )

            st.write(
                "**Area:**",
                incident["area"]
            )

            st.write(
                "**Location:**",
                f"{incident['lat']}, "
                f"{incident['lon']}"
            )

            st.write(
                "**AI Assistance:**",
                incident["ai"]
            )

            if incident["image_name"]:

                st.write(
                    "**Uploaded Image:**",
                    incident["image_name"]
                )

            st.divider()

            st.subheader(
                "📍 Nearby Eligible Responders"
            )

            responders = find_nearby_responders(
                incident
            )

            if responders:

                for distance, team in responders:

                    st.write(
                        f"- **{team}** — "
                        f"{distance:.1f} km away"
                    )

            else:

                st.warning(
                    "No available eligible "
                    "responder found nearby."
                )

            col1, col2, col3 = st.columns(3)

            with col1:

                if st.button(
                    "🚒 Assign Nearest",
                    key=f"assign_{incident['id']}"
                ):

                    if responders:

                        nearest_team = (
                            responders[0][1]
                        )

                        incident[
                            "responder"
                        ] = nearest_team

                        incident[
                            "status"
                        ] = "Assigned"

                        for responder in (
                            st.session_state.responders
                        ):

                            if (
                                responder["name"]
                                == nearest_team
                            ):

                                responder[
                                    "available"
                                ] = False

                        st.success(
                            f"Assigned to "
                            f"{nearest_team}"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "No eligible responder."
                        )

            with col2:

                if st.button(
                    "🔔 Escalate",
                    key=f"escalate_{incident['id']}"
                ):

                    incident[
                        "status"
                    ] = "Escalated"

                    st.success(
                        "Incident escalated."
                    )

            with col3:

                if st.button(
                    "✅ Resolve",
                    key=f"resolve_{incident['id']}"
                ):

                    incident[
                        "status"
                    ] = "Resolved"

                    st.rerun()


# ============================================================
# RESPONDER DASHBOARD
# ============================================================

else:

    st.title(
        "🚒 Responder Dashboard"
    )

    st.write(
        "Responders see incidents "
        "assigned to their team."
    )

    responder_names = [
        responder["name"]
        for responder
        in st.session_state.responders
    ]

    selected_team = st.selectbox(
        "Responder Team",
        responder_names
    )

    assigned_incidents = [

        incident

        for incident
        in st.session_state.incidents

        if incident["responder"]
        == selected_team
    ]

    if not assigned_incidents:

        st.info(
            "No assigned incidents."
        )

    for incident in assigned_incidents:

        st.subheader(
            f"🚨 {incident['id']} — "
            f"{incident['type']}"
        )

        st.write(
            "**Location:**",
            f"{incident['lat']}, "
            f"{incident['lon']}"
        )

        st.write(
            "**Description:**",
            incident["description"]
        )

        st.write(
            "**Current Status:**",
            incident["status"]
        )

        new_status = st.selectbox(
            "Update Status",

            [
                "Assigned",
                "Accepted",
                "En Route",
                "On Scene",
                "Response Completed"
            ],

            key=f"status_{incident['id']}"
        )

        if st.button(
            "🔄 Update Status",
            key=f"update_{incident['id']}"
        ):

            incident[
                "status"
            ] = new_status

            if (
                new_status
                == "Response Completed"
            ):

                for responder in (
                    st.session_state.responders
                ):

                    if (
                        responder["name"]
                        == selected_team
                    ):

                        responder[
                            "available"
                        ] = True

            st.success(
                "Status updated."
            )

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Emergency Response Platform | "
    "Educational Prototype"
)
