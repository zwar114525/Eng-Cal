"""
Streamlit Web UI for Engineering Intake System.
"""

import streamlit as st
import json
from pathlib import Path

from modules.intake import EngineeringIntake
from modules.enums import JobType, Jurisdiction
from modules.code_database import CodeDatabase
from config.manager import ConfigManager, get_config_manager


# Page config
st.set_page_config(
    page_title="Engineering Freelance AI Agent",
    page_icon="",
    layout="wide"
)


def init_session_state():
    """Initialize session state variables"""
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = get_config_manager()
    if 'llm_client' not in st.session_state:
        st.session_state.llm_client = None
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'available_models' not in st.session_state:
        st.session_state.available_models = []


def render_llm_config_tab():
    """Render LLM Configuration tab"""
    st.header("LLM Configuration")
    
    config = st.session_state.config_manager
    
    # Current status
    is_configured = config.is_llm_configured()
    status_color = "green" if is_configured else "red"
    status_text = "Configured" if is_configured else "Not Configured"
    st.markdown(f"**Status:** :{status_color}[{status_text}]")
    
    # When base_url is already configured but we have no cached models, fetch once so dropdown is useful
    base_url = config.get_llm_base_url()
    if base_url and base_url.strip() and not st.session_state.available_models and config.get_llm_api_key():
        fetched = config.fetch_models_from_base_url(base_url, config.get_llm_api_key())
        if fetched:
            st.session_state.available_models = fetched
    
    DEFAULT_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "claude-sonnet-4-5-20250929", "claude-haiku-3-5-20250929"]
    model_options = st.session_state.available_models if st.session_state.available_models else DEFAULT_MODELS
    current_model = config.get_llm_model()
    try:
        model_default_index = model_options.index(current_model)
    except ValueError:
        model_default_index = 0

    with st.form("llm_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            provider = st.selectbox(
                "Provider",
                ["openai", "anthropic", "custom"],
                index=["openai", "anthropic", "custom"].index(config.get_llm_provider()) if config.get_llm_provider() in ["openai", "anthropic", "custom"] else 0
            )
            
            base_url = st.text_input(
                "Base URL (optional)",
                value=config.get_llm_base_url(),
                placeholder="https://api.openrouter.ai/v1 for OpenRouter"
            )
        
        with col2:
            api_key = st.text_input(
                "API Key",
                value=config.get_llm_api_key() if config.get_llm_api_key() else "",
                type="password",
                placeholder="Enter your API key"
            )
            
            model = st.selectbox(
                "Model",
                model_options,
                index=model_default_index,
                help="When using OpenRouter or a custom base URL, save configuration to load available models here."
            )
        
        submitted = st.form_submit_button("Save Configuration")
        
        if submitted:
            # If base_url is set, fetch models from endpoint and switch to dropdown for next time
            if base_url and base_url.strip():
                with st.spinner("Fetching available models from base URL..."):
                    fetched = config.fetch_models_from_base_url(base_url.strip(), api_key or "")
                if fetched:
                    st.session_state.available_models = fetched
                    # Keep selected model if it's in the new list, otherwise use first available
                    model_to_save = model if model in fetched else fetched[0]
                else:
                    st.session_state.available_models = []
                    model_to_save = model
            else:
                st.session_state.available_models = []
                model_to_save = model
            config.set_llm_config(provider, base_url.strip(), api_key, model_to_save)
            st.success("Configuration saved successfully!" + (" Models from base URL loaded." if (base_url and base_url.strip() and st.session_state.available_models) else ""))
            # Recreate client
            st.session_state.llm_client = config.create_llm_client()
    
    # Test connection
    st.divider()
    st.subheader("Test Connection")
    
    if st.button("Test LLM Connection"):
        with st.spinner("Testing connection..."):
            client = config.create_llm_client()
            if client:
                try:
                    # Simple test
                    if hasattr(client, 'chat'):
                        response = client.chat.completions.create(
                            model=config.get_llm_model(),
                            messages=[{"role": "user", "content": "Hello"}],
                            max_tokens=10
                        )
                        st.success(f"Connection successful! Response: {response.choices[0].message.content}")
                    elif hasattr(client, 'messages'):
                        response = client.messages.create(
                            model=config.get_llm_model(),
                            max_tokens=10,
                            messages=[{"role": "user", "content": "Hello"}]
                        )
                        st.success("Connection successful with Anthropic!")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
            else:
                st.error("Failed to create client. Please check your configuration.")


def render_job_intake_tab():
    """Render Job Intake tab"""
    st.header("Job Intake")
    
    config = st.session_state.config_manager
    
    # Job text input
    job_text = st.text_area(
        "Paste Job Description",
        height=200,
        placeholder="Enter the job posting text here..."
    )
    
    # Sample jobs
    with st.expander("Sample Jobs"):
        st.code("""Need pile foundation design for 1300 sft residential slab in Mumbai. 
Soil report available. Must follow IS 2911. Deliverables: DWG layout + Excel calcs.
Budget: 8000 INR.""", language="text")
        st.code("""Need permit-ready patio roof plans for Palmetto Bay, FL. 
Aluminum structure, 40x12 ft. Must be PE stamped for Florida.""", language="text")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        parse_button = st.button("Parse Job", type="primary")
    
    if parse_button and job_text:
        with st.spinner("Processing job..."):
            llm_client = config.create_llm_client()
            try:
                intake = EngineeringIntake(
                    raw_text=job_text,
                    llm_client=llm_client,
                    llm_provider=config.get_llm_provider(),
                    base_url=config.get_llm_base_url(),
                    model=config.get_llm_model(),
                )
            except TypeError:
                intake = EngineeringIntake(
                    raw_text=job_text,
                    llm_client=llm_client,
                    llm_provider=config.get_llm_provider(),
                    base_url=config.get_llm_base_url(),
                )
            
            result = intake.parse_to_structured()
            st.session_state.result = result
            
            # Save to log
            if config.require_audit_log():
                log_file = intake.save_intake_log()
                st.info(f"Log saved to: {log_file}")
    
    # Display results
    if st.session_state.result:
        result = st.session_state.result
        
        st.divider()
        
        # Classification
        st.subheader("Classification")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Job Type", result["classification"]["job_type"])
        with col2:
            st.metric("Jurisdiction", result["classification"]["jurisdiction"])
        
        st.caption(f"Confidence: {result['classification']['confidence']}")
        
        # Required Codes
        st.subheader("Required Codes")
        codes = result["required_codes"]["codes"]
        if codes:
            for code in codes:
                with st.expander(f"{code['code_id']} - {code['priority'].upper()}"):
                    st.markdown(f"**Title:** {code['title']}")
                    st.markdown(f"**Scope:** {code['scope']}")
                    st.markdown(f"**Edition:** {code.get('edition', 'latest')}")
                    if code.get('source_url'):
                        st.markdown(f"[Source]({code['source_url']})")
        else:
            st.warning("No codes identified - manual research required")
        
        st.caption(f"Source: {result['required_codes']['source']}")
        
        # Requirements
        st.subheader("Requirements")
        st.markdown("**Deliverables:**")
        for d in result["requirements"]["deliverables"]:
            st.write(f"- {d}")
        
        st.markdown("**Missing Inputs:**")
        for inp in result["requirements"]["required_inputs_missing"]:
            st.write(f"- {inp}")
        
        lic = result["requirements"]["licensing"]
        st.markdown(f"**License Required:** {lic['requires_license']}")
        if lic['requires_license']:
            st.markdown(f"**License Type:** {lic['license_type']}")
        
        # Risk Assessment
        st.subheader("Risk Assessment")
        risk_level = result["risk_assessment"]["overall_risk"]
        risk_color = "red" if risk_level == "high" else "green"
        st.markdown(f"**Overall Risk:** :{risk_color}[{risk_level.upper()}]")
        
        for flag in result["risk_assessment"]["flags"]:
            st.write(f"- {flag}")
        
        # Next Actions
        st.subheader("Next Actions")
        st.markdown(f"**Recommended First Step:** {result['next_actions']['recommended_first_step']}")
        
        st.markdown("**Clarifying Questions:**")
        for q in result["next_actions"]["clarifying_questions"]:
            st.write(f"- {q}")
        
        # Compliance
        st.divider()
        st.warning(result["compliance"]["disclaimer"])


def render_code_lookup_tab():
    """Render Code Lookup tab"""
    st.header("Code Lookup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_jurisdiction = st.selectbox(
            "Jurisdiction",
            [j.value for j in Jurisdiction]
        )
    
    with col2:
        selected_job_type = st.selectbox(
            "Job Type",
            [j.value for j in JobType]
        )
    
    if st.button("Lookup Codes"):
        codes = CodeDatabase.get_required_codes(selected_jurisdiction, selected_job_type)
        
        if codes:
            st.success(f"Found {len(codes)} codes")
            for code in codes:
                with st.expander(f"{code.code_id} - {code.priority.upper()}"):
                    st.markdown(f"**Title:** {code.title}")
                    st.markdown(f"**Scope:** {code.scope}")
                    st.markdown(f"**Edition:** {code.edition}")
                    if code.parts:
                        st.markdown("**Parts:**")
                        for part in code.parts:
                            st.write(f"- {part}")
                    if code.source_url:
                        st.markdown(f"[Source]({code.source_url})")
        else:
            st.warning("No codes found for this combination")
    
    # Browse all codes
    st.divider()
    st.subheader("Browse All Codes")
    
    if st.button("Show All Codes"):
        all_codes = CodeDatabase.get_all_codes()
        st.success(f"Total codes: {len(all_codes)}")
        
        for code in all_codes[:20]:  # Limit display
            with st.expander(f"{code.code_id}"):
                st.markdown(f"**Title:** {code.title}")
                st.markdown(f"**Scope:** {code.scope}")
                st.markdown(f"**Priority:** {code.priority}")


def main():
    """Main application"""
    init_session_state()
    
    st.title("Engineering Freelance AI Agent")
    st.markdown("Module 1: Generalized Intake & Config")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["LLM Configuration", "Job Intake", "Code Lookup"])
    
    with tab1:
        render_llm_config_tab()
    
    with tab2:
        render_job_intake_tab()
    
    with tab3:
        render_code_lookup_tab()


if __name__ == "__main__":
    main()
