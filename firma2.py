import datetime
current_year = datetime.datetime.now().year
# ... na konec souboru
import streamlit as st
st.markdown(f"<hr style='margin-top:2em;margin-bottom:0.5em;'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:gray; font-size:0.95em;'>© {current_year} Tomáš Paleta, Masarykova univerzita, Ekonomicko-správní fakulta, Brno</div>", unsafe_allow_html=True)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Firm Equilibrium Simulator", layout="wide")

# CSS styling
st.markdown("""
    <style>
    .header {font-size: 28px; font-weight: bold; color: #1f77b4;}
    .subheader {font-size: 18px; font-weight: bold; color: #2ca02c;}
    .info-box {background-color: #e7f3ff; padding: 15px; border-radius: 5px; border-left: 4px solid #2196F3;}
    .warning-box {background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Firm Equilibrium Interactive Simulator")
st.markdown("*Learn how firms optimize output and pricing across different market structures**")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Topic:", [
    "Introduction",
    "Perfect Competition",
    "Monopoly",
    "Duopoly",
    "Monopolistic Competition",
    "Comparison Tool"
])

# ===================== INTRODUCTION PAGE =====================
if page == "Introduction":
    st.markdown("### 🎓 Understanding Firm Equilibrium")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-box">
        <b>What is Firm Equilibrium?</b><br>
        Firm equilibrium occurs when a firm maximizes profit by producing where:
        <b>Marginal Revenue (MR) = Marginal Cost (MC)</b>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <b>Key Concepts:</b><br>
        • <b>Total Revenue (TR):</b> Price × Quantity<br>
        • <b>Total Cost (TC):</b> Fixed Cost + (Variable Cost × Q)<br>
        • <b>Profit:</b> TR - TC<br>
        • <b>Marginal Revenue:</b> Change in TR from 1 unit<br>
        • <b>Marginal Cost:</b> Change in TC from 1 unit
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 Market Structures Overview")
    
    market_data = {
        "Feature": ["Number of Firms", "Product Type", "Barriers to Entry", "Price Power", "Long-run Profit"],
        "Perfect Competition": ["Many", "Homogeneous", "None", "None (Price taker)", "Zero"],
        "Monopolistic Competition": ["Many", "Differentiated", "Low", "Some", "Zero"],
        "Duopoly": ["Two", "Variable", "High", "Significant", "Positive"],
        "Monopoly": ["One", "Unique", "Very High", "Complete", "Positive"]
    }
    
    df_markets = pd.DataFrame(market_data)
    st.table(df_markets)

# ===================== PERFECT COMPETITION PAGE =====================
elif page == "Perfect Competition":
    st.markdown("### 🏛️ Perfect Competition Model")
    
    st.markdown("""
    <div class="info-box">
    <b>Characteristics:</b>
    • Many buyers and sellers
    • Homogeneous (identical) products
    • Firms are price takers (cannot influence price)
    • Free entry and exit
    • Perfect information
    • Long-run: Zero economic profit (P = AC)
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Input Parameters")
        market_price = st.slider("Market Price (determined by supply/demand)", 5.0, 50.0, 20.0, key="pc_price")
        fixed_cost_pc = st.number_input("Fixed Costs ($)", min_value=0.0, value=100.0, key="pc_fc")
        var_cost_pc = st.slider("Variable Cost per Unit ($)", 1.0, 20.0, 10.0, key="pc_vc")
        quantity_pc = st.slider("Quantity Produced (units)", 0, 100, 50, key="pc_q")
    
    with col2:
        # Calculations for perfect competition
        tr_pc = market_price * quantity_pc
        tc_pc = fixed_cost_pc + (var_cost_pc * quantity_pc)
        profit_pc = tr_pc - tc_pc
        ac_pc = tc_pc / quantity_pc if quantity_pc > 0 else 0
        avc_pc = (var_cost_pc * quantity_pc) / quantity_pc if quantity_pc > 0 else var_cost_pc
        mr_pc = market_price  # In perfect competition, MR = Price
        
        st.markdown("#### Financial Analysis")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Total Revenue", f"${tr_pc:,.2f}")
            st.metric("Total Cost", f"${tc_pc:,.2f}")
            st.metric("Average Cost (AC)", f"${ac_pc:.2f}")
        with col_b:
            st.metric("Profit/Loss", f"${profit_pc:,.2f}", delta=profit_pc)
            st.metric("Marginal Revenue (Price)", f"${mr_pc:.2f}")
            st.metric("Variable Cost per Unit", f"${var_cost_pc:.2f}")
        
        # Color-coded message
        if profit_pc > 0:
            st.success(f"✅ Profitable! The firm earns ${profit_pc:,.2f}")
        elif profit_pc == 0:
            st.info("⚪ Break-even point reached")
        else:
            st.warning(f"❌ Loss of ${abs(profit_pc):,.2f}")
    
    st.markdown("---")
    
    # Visualization
    st.markdown("#### 📊 Cost and Revenue Analysis")
    
    quantities = np.arange(0, 101, 1)
    tr_values = market_price * quantities
    tc_values = fixed_cost_pc + (var_cost_pc * quantities)
    profit_values = tr_values - tc_values
    ac_values = tc_values / (quantities + 1e-10)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Chart 1: TR, TC, and Profit
    axes[0].plot(quantities, tr_values, label="Total Revenue", linewidth=2, color='green')
    axes[0].plot(quantities, tc_values, label="Total Cost", linewidth=2, color='red')
    axes[0].axhline(y=0, color='black', linestyle='--', alpha=0.3)
    axes[0].scatter([quantity_pc], [tr_pc], color='green', s=100, zorder=5)
    axes[0].scatter([quantity_pc], [tc_pc], color='red', s=100, zorder=5)
    axes[0].set_xlabel("Quantity (units)")
    axes[0].set_ylabel("$ Amount")
    axes[0].set_title("Total Revenue vs Total Cost")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Chart 2: Price, MC, and AC
    mc_values = np.array([var_cost_pc] * len(quantities))  # MC = VC in perfect competition
    axes[1].axhline(y=market_price, label="Price = MR", linewidth=2, color='blue')
    axes[1].plot(quantities[1:], mc_values[1:], label="Marginal Cost (MC)", linewidth=2, color='orange')
    axes[1].plot(quantities[1:], ac_values[1:], label="Average Cost (AC)", linewidth=2, color='red')
    axes[1].scatter([quantity_pc], [market_price], color='blue', s=100, zorder=5, label="Equilibrium")
    axes[1].set_xlabel("Quantity (units)")
    axes[1].set_ylabel("$ per Unit")
    axes[1].set_title("Price, MR, MC, and AC")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    axes[1].set_ylim(0, 40)
    
    st.pyplot(fig)
    
    st.markdown("""
    <div class="info-box">
    <b>📌 Key Insight:</b><br>
    In perfect competition, firms are price takers. The equilibrium output occurs where Price (MR) = MC. 
    In the long run, free entry drives profits to zero as more firms enter if profits are positive.
    </div>
    """, unsafe_allow_html=True)

# ===================== MONOPOLY PAGE =====================
elif page == "Monopoly":
    st.markdown("### 🏰 Monopoly Model")
    
    st.markdown("""
    <div class="info-box">
    <b>Characteristics:</b>
    • Single seller (firm is the entire industry)
    • Unique product with no substitutes
    • Price maker (can set price)
    • High barriers to entry
    • Can earn long-run economic profit
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Market & Cost Parameters")
        demand_intercept = st.slider("Demand Intercept (Max Price)", 50.0, 100.0, 80.0, key="mono_demand")
        demand_slope = st.slider("Demand Slope (steepness)", 0.1, 2.0, 0.5, key="mono_slope")
        fixed_cost_mono = st.number_input("Fixed Costs ($)", min_value=0.0, value=100.0, key="mono_fc")
        var_cost_mono = st.slider("Variable Cost per Unit ($)", 1.0, 20.0, 10.0, key="mono_vc")
        quantity_mono = st.slider("Quantity to Produce (units)", 0, 100, 40, key="mono_q")
    
    with col2:
        # Calculate for monopoly
        price_mono = demand_intercept - (demand_slope * quantity_mono)
        price_mono = max(price_mono, 0)  # Price cannot be negative
        
        tr_mono = price_mono * quantity_mono
        tc_mono = fixed_cost_mono + (var_cost_mono * quantity_mono)
        profit_mono = tr_mono - tc_mono
        ac_mono = tc_mono / quantity_mono if quantity_mono > 0 else 0
        
        # MR calculation for monopoly
        if quantity_mono > 0:
            mr_mono = demand_intercept - (2 * demand_slope * quantity_mono)
        else:
            mr_mono = demand_intercept
        
        st.markdown("#### Financial Analysis")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Price (Set by Firm)", f"${price_mono:.2f}")
            st.metric("Total Revenue", f"${tr_mono:,.2f}")
            st.metric("Total Cost", f"${tc_mono:,.2f}")
        with col_b:
            st.metric("Profit/Loss", f"${profit_mono:,.2f}", delta=profit_mono)
            st.metric("Marginal Revenue (MR)", f"${mr_mono:.2f}")
            st.metric("Average Cost (AC)", f"${ac_mono:.2f}")
        
        if profit_mono > 0:
            st.success(f"✅ Strong Profit! The monopolist earns ${profit_mono:,.2f}")
        elif profit_mono == 0:
            st.info("⚪ Break-even point")
        else:
            st.warning(f"❌ Loss of ${abs(profit_mono):,.2f}")
    
    st.markdown("---")
    
    # Visualization
    st.markdown("#### 📊 Monopoly Equilibrium Analysis")
    
    quantities_mono = np.arange(0, 101, 1)
    prices_mono = np.maximum(demand_intercept - (demand_slope * quantities_mono), 0)
    tr_values_mono = prices_mono * quantities_mono
    tc_values_mono = fixed_cost_mono + (var_cost_mono * quantities_mono)
    profit_values_mono = tr_values_mono - tc_values_mono
    
    # MR calculation
    mr_values_mono = demand_intercept - (2 * demand_slope * quantities_mono)
    mr_values_mono = np.maximum(mr_values_mono, -20)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Chart 1: Demand and MR curves
    axes[0].plot(quantities_mono, prices_mono, label="Demand Curve", linewidth=2.5, color='blue')
    axes[0].plot(quantities_mono, mr_values_mono, label="Marginal Revenue (MR)", linewidth=2.5, color='purple', linestyle='--')
    axes[0].scatter([quantity_mono], [price_mono], color='red', s=150, zorder=5, label="Monopoly Price & Quantity")
    axes[0].axhline(y=var_cost_mono, label="MC (= VC)", linewidth=2, color='orange')
    axes[0].set_xlabel("Quantity (units)")
    axes[0].set_ylabel("Price ($)")
    axes[0].set_title("Demand, MR, and MC Curves")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[0].set_ylim(-10, 100)
    
    # Chart 2: Profit curve
    axes[1].plot(quantities_mono, profit_values_mono, linewidth=2.5, color='green')
    axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1].scatter([quantity_mono], [profit_mono], color='red', s=150, zorder=5, label=f"Current: ${profit_mono:.2f}")
    axes[1].fill_between(quantities_mono, 0, profit_values_mono, where=(profit_values_mono > 0), alpha=0.3, color='green')
    axes[1].fill_between(quantities_mono, 0, profit_values_mono, where=(profit_values_mono <= 0), alpha=0.3, color='red')
    axes[1].set_xlabel("Quantity (units)")
    axes[1].set_ylabel("Profit ($)")
    axes[1].set_title("Profit Curve")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    st.pyplot(fig)
    
    # Find optimal quantity (where MR = MC)
    optimal_idx = np.argmin(np.abs(mr_values_mono - var_cost_mono))
    optimal_q = quantities_mono[optimal_idx]
    optimal_price = prices_mono[optimal_idx]
    optimal_profit = tr_values_mono[optimal_idx] - tc_values_mono[optimal_idx]
    
    st.markdown(f"""
    <div class="info-box">
    <b>📌 Monopoly Optimization:</b><br>
    <b>Profit-maximizing output:</b> {optimal_q} units at price ${optimal_price:.2f}, yielding ${optimal_profit:.2f} profit<br>
    <b>Current output:</b> {quantity_mono} units at price ${price_mono:.2f}, yielding ${profit_mono:.2f} profit<br>
    <b>Note:</b> Monopolies can sustain long-run profits due to barriers to entry!
    </div>
    """, unsafe_allow_html=True)

# ===================== DUOPOLY PAGE =====================
elif page == "Duopoly":
    st.markdown("### 👥 Duopoly Model (Cournot Competition)")
    
    st.markdown("""
    <div class="info-box">
    <b>Characteristics:</b>
    • Exactly two firms in the market
    • Each firm chooses quantity independently
    • Firms consider rival's reaction when deciding output
    • Cournot model: firms choose quantity simultaneously
    • Firms have partial price power
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("#### Market Parameters")
        demand_int_duo = st.slider("Market Demand Intercept", 50.0, 100.0, 80.0, key="duo_demand")
        demand_slope_duo = st.slider("Demand Slope", 0.1, 1.0, 0.5, key="duo_slope")
    
    with col2:
        st.markdown("#### Firm A (Your Firm)")
        q_a = st.slider("Firm A's Output", 0, 50, 25, key="duo_qa")
        fc_a = st.number_input("Firm A Fixed Costs", min_value=0.0, value=50.0, key="duo_fc_a")
        vc_a = st.slider("Firm A Variable Cost/unit", 1.0, 20.0, 10.0, key="duo_vc_a")
    
    with col3:
        st.markdown("#### Firm B (Competitor)")
        q_b = st.slider("Firm B's Output", 0, 50, 25, key="duo_qb")
        fc_b = st.number_input("Firm B Fixed Costs", min_value=0.0, value=50.0, key="duo_fc_b")
        vc_b = st.slider("Firm B Variable Cost/unit", 1.0, 20.0, 10.0, key="duo_vc_b")
    
    st.markdown("---")
    
    # Calculate market price and profits
    total_quantity_duo = q_a + q_b
    market_price_duo = demand_int_duo - (demand_slope_duo * total_quantity_duo)
    market_price_duo = max(market_price_duo, 0)
    
    tr_a = market_price_duo * q_a
    tc_a = fc_a + (vc_a * q_a)
    profit_a = tr_a - tc_a
    
    tr_b = market_price_duo * q_b
    tc_b = fc_b + (vc_b * q_b)
    profit_b = tr_b - tc_b
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Market Result")
        st.metric("Market Price", f"${market_price_duo:.2f}")
        st.metric("Total Industry Output", f"{total_quantity_duo} units")
    
    with col2:
        st.markdown("#### Firm A Performance")
        st.metric("Revenue", f"${tr_a:,.2f}")
        st.metric("Cost", f"${tc_a:,.2f}")
        st.metric("Profit", f"${profit_a:,.2f}", delta=profit_a)
    
    with col3:
        st.markdown("#### Firm B Performance")
        st.metric("Revenue", f"${tr_b:,.2f}")
        st.metric("Cost", f"${tc_b:,.2f}")
        st.metric("Profit", f"${profit_b:,.2f}", delta=profit_b)
    
    st.markdown("---")
    st.markdown("#### 📊 Duopoly Reaction Function")
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Reaction functions
    q_a_range = np.linspace(0, 50, 100)
    q_b_range = np.linspace(0, 50, 100)
    
    # Firm A's best response to Firm B (simplified)
    best_response_a = (demand_int_duo - vc_a - (demand_slope_duo * q_b_range)) / (2 * demand_slope_duo)
    best_response_a = np.clip(best_response_a, 0, 50)
    
    best_response_b = (demand_int_duo - vc_b - (demand_slope_duo * q_a_range)) / (2 * demand_slope_duo)
    best_response_b = np.clip(best_response_b, 0, 50)
    
    ax.plot(q_a_range, best_response_b, label="Firm B's Reaction Function", linewidth=2.5, color='red')
    ax.plot(best_response_a, q_b_range, label="Firm A's Reaction Function", linewidth=2.5, color='blue')
    ax.scatter([q_a], [q_b], s=200, color='green', zorder=5, label="Current Position", marker='*')
    
    ax.set_xlabel("Firm A Output (units)")
    ax.set_ylabel("Firm B Output (units)")
    ax.set_title("Cournot Duopoly: Reaction Functions")
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 50)
    
    st.pyplot(fig)
    
    st.markdown("""
    <div class="info-box">
    <b>📌 Duopoly Dynamics:</b><br>
    In Cournot competition, each firm's optimal output depends on what the rival produces (reaction function).
    The intersection of both reaction functions is the Nash Equilibrium—where neither firm wants to change output given the other's choice.
    </div>
    """, unsafe_allow_html=True)

# ===================== MONOPOLISTIC COMPETITION PAGE =====================
elif page == "Monopolistic Competition":
    st.markdown("### 🏪 Monopolistic Competition Model")
    
    st.markdown("""
    <div class="info-box">
    <b>Characteristics:</b>
    • Many firms with differentiated products
    • Each firm has some price power (downward-sloping demand)
    • Free entry and exit
    • Long-run: Zero economic profit (P = AC)
    • Short-run: Can earn positive or negative profit
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Short-Run Analysis")
        demand_int_mc = st.slider("Firm's Demand Intercept", 30.0, 80.0, 50.0, key="mc_demand")
        demand_slope_mc = st.slider("Demand Slope", 0.1, 1.0, 0.3, key="mc_slope")
        fixed_cost_mc = st.number_input("Fixed Costs ($)", min_value=0.0, value=100.0, key="mc_fc")
        var_cost_mc = st.slider("Variable Cost/unit", 1.0, 20.0, 10.0, key="mc_vc")
        quantity_mc = st.slider("Quantity Produced", 0, 80, 40, key="mc_q")
    
    with col2:
        price_mc = demand_int_mc - (demand_slope_mc * quantity_mc)
        price_mc = max(price_mc, 0)
        
        tr_mc = price_mc * quantity_mc
        tc_mc = fixed_cost_mc + (var_cost_mc * quantity_mc)
        profit_mc = tr_mc - tc_mc
        ac_mc = tc_mc / quantity_mc if quantity_mc > 0 else 0
        
        st.markdown("#### Short-Run Results")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Price", f"${price_mc:.2f}")
            st.metric("Total Revenue", f"${tr_mc:,.2f}")
            st.metric("AC per unit", f"${ac_mc:.2f}")
        with col_b:
            st.metric("Profit/Loss", f"${profit_mc:,.2f}", delta=profit_mc)
            st.metric("Surplus/Deficit", "Positive" if profit_mc > 0 else "Negative")
    
    st.markdown("---")
    st.markdown("#### 📊 Short-Run vs Long-Run Equilibrium")
    
    quantities_mc = np.arange(1, 81, 1)
    prices_mc = np.maximum(demand_int_mc - (demand_slope_mc * quantities_mc), 0)
    tr_values_mc = prices_mc * quantities_mc
    tc_values_mc = fixed_cost_mc + (var_cost_mc * quantities_mc)
    profit_values_mc = tr_values_mc - tc_values_mc
    ac_values_mc = tc_values_mc / quantities_mc
    
    # Long-run: where P = AC
    breakeven_q = np.where(np.abs(prices_mc - ac_values_mc) < 1)[0]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Chart 1: Demand, MR, MC, AC
    mr_values_mc = demand_int_mc - (2 * demand_slope_mc * quantities_mc)
    axes[0].plot(quantities_mc, prices_mc, label="Demand (Price)", linewidth=2.5, color='blue')
    axes[0].plot(quantities_mc, mr_values_mc, label="Marginal Revenue (MR)", linewidth=2, color='purple', linestyle='--')
    axes[0].axhline(y=var_cost_mc, label="MC", linewidth=2, color='orange')
    axes[0].plot(quantities_mc, ac_values_mc, label="Average Cost (AC)", linewidth=2, color='red')
    axes[0].scatter([quantity_mc], [price_mc], color='darkblue', s=150, zorder=5, label="Short-run")
    axes[0].set_xlabel("Quantity (units)")
    axes[0].set_ylabel("$ per Unit")
    axes[0].set_title("Short-Run Equilibrium (P > AC = Profit)")
    axes[0].legend(fontsize=10)
    axes[0].grid(alpha=0.3)
    axes[0].set_ylim(0, 50)
    
    # Chart 2: Profit curve
    axes[1].plot(quantities_mc, profit_values_mc, linewidth=2.5, color='green')
    axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1].scatter([quantity_mc], [profit_mc], color='darkblue', s=150, zorder=5, label="Short-run profit")
    axes[1].fill_between(quantities_mc, 0, profit_values_mc, where=(profit_values_mc > 0), alpha=0.3, color='green', label="Profit region")
    axes[1].fill_between(quantities_mc, 0, profit_values_mc, where=(profit_values_mc <= 0), alpha=0.3, color='red', label="Loss region")
    axes[1].set_xlabel("Quantity (units)")
    axes[1].set_ylabel("Profit ($)")
    axes[1].set_title("Profit Curve: Short-Run vs Long-Run")
    axes[1].legend(fontsize=10)
    axes[1].grid(alpha=0.3)
    
    st.pyplot(fig)
    
    st.markdown(f"""
    <div class="info-box">
    <b>📌 Long-Run Adjustment:</b><br>
    <b>Short-run:</b> Firm earns ${profit_mc:.2f} profit<br>
    <b>Long-run expectation:</b> Positive profits attract new entrants → market demand shifts → profit → 0 (P = AC)<br>
    <b>Long-run equilibrium:</b> Zero economic profit, but P > MC (unlike perfect competition)
    </div>
    """, unsafe_allow_html=True)

# ===================== COMPARISON PAGE =====================
elif page == "Comparison Tool":
    st.markdown("### 🔄 Compare Market Structures")
    
    st.markdown("""
    <div class="info-box">
    <b>Use this tool to compare how firms respond to the same cost and demand conditions across different market structures.</b>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Common Parameters")
        price_level = st.slider("Base Price Level", 20.0, 50.0, 30.0, key="comp_price")
        fixed_cost_comp = st.number_input("Fixed Costs", min_value=0.0, value=100.0, key="comp_fc")
        var_cost_comp = st.slider("Variable Cost/unit", 1.0, 20.0, 10.0, key="comp_vc")
    
    with col2:
        st.markdown("#### Production Quantity for Each Structure")
        q_pc_comp = st.slider("Perfect Competition Output", 0, 100, 30, key="comp_pc_q")
        q_mono_comp = st.slider("Monopoly Output", 0, 100, 20, key="comp_mono_q")
        q_duo_comp = st.slider("Duopoly (each firm) Output", 0, 50, 20, key="comp_duo_q")
        q_mc_comp = st.slider("Monopolistic Competition Output", 0, 100, 25, key="comp_mc_q")
    
    st.markdown("---")
    
    # Calculate outcomes for each structure
    comp_data = []
    
    # Perfect Competition
    tr_pc_comp = price_level * q_pc_comp
    tc_pc_comp = fixed_cost_comp + (var_cost_comp * q_pc_comp)
    profit_pc_comp = tr_pc_comp - tc_pc_comp
    comp_data.append({
        "Market Structure": "Perfect Competition",
        "Price": f"${price_level:.2f}",
        "Quantity": q_pc_comp,
        "Total Revenue": f"${tr_pc_comp:,.0f}",
        "Total Cost": f"${tc_pc_comp:,.0f}",
        "Profit": f"${profit_pc_comp:,.0f}",
        "Consumer Surplus": "Max ✅"
    })
    
    # Monopoly (higher price, lower quantity)
    price_mono_comp = price_level * 1.3  # Markup
    tr_mono_comp = price_mono_comp * q_mono_comp
    tc_mono_comp = fixed_cost_comp + (var_cost_comp * q_mono_comp)
    profit_mono_comp = tr_mono_comp - tc_mono_comp
    comp_data.append({
        "Market Structure": "Monopoly",
        "Price": f"${price_mono_comp:.2f}",
        "Quantity": q_mono_comp,
        "Total Revenue": f"${tr_mono_comp:,.0f}",
        "Total Cost": f"${tc_mono_comp:,.0f}",
        "Profit": f"${profit_mono_comp:,.0f}",
        "Consumer Surplus": "Min ❌"
    })
    
    # Duopoly
    price_duo_comp = price_level * 1.15
    tr_duo_comp = price_duo_comp * q_duo_comp * 2
    tc_duo_comp = fixed_cost_comp + (var_cost_comp * q_duo_comp)
    profit_duo_comp = (tr_duo_comp / 2) - tc_duo_comp
    comp_data.append({
        "Market Structure": "Duopoly (per firm)",
        "Price": f"${price_duo_comp:.2f}",
        "Quantity": q_duo_comp,
        "Total Revenue": f"${tr_duo_comp/2:,.0f}",
        "Total Cost": f"${tc_duo_comp:,.0f}",
        "Profit": f"${profit_duo_comp:,.0f}",
        "Consumer Surplus": "Medium 🟡"
    })
    
    # Monopolistic Competition
    tr_mc_comp = price_level * 1.1 * q_mc_comp
    tc_mc_comp = fixed_cost_comp + (var_cost_comp * q_mc_comp)
    profit_mc_comp = tr_mc_comp - tc_mc_comp
    comp_data.append({
        "Market Structure": "Monopolistic Competition",
        "Price": f"${price_level * 1.1:.2f}",
        "Quantity": q_mc_comp,
        "Total Revenue": f"${tr_mc_comp:,.0f}",
        "Total Cost": f"${tc_mc_comp:,.0f}",
        "Profit": f"${profit_mc_comp:,.0f}",
        "Consumer Surplus": "High ✅"
    })
    
    df_comparison = pd.DataFrame(comp_data)
    st.table(df_comparison)
    
    st.markdown("---")
    st.markdown("#### 📊 Profit Comparison")
    
    profits_comp = [profit_pc_comp, profit_mono_comp, profit_duo_comp, profit_mc_comp]
    structures = ["Perfect\nCompetition", "Monopoly", "Duopoly", "Monopolistic\nCompetition"]
    colors = ['green' if p >= 0 else 'red' for p in profits_comp]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(structures, profits_comp, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_ylabel("Profit ($)", fontsize=12)
    ax.set_title("Firm Profit by Market Structure", fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, profit in zip(bars, profits_comp):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${profit:,.0f}',
                ha='center', va='bottom' if height > 0 else 'top', fontweight='bold')
    
    st.pyplot(fig)
    
    st.markdown("""
    <div class="info-box">
    <b>📌 Key Takeaways:</b><br>
    • <b>Perfect Competition:</b> P = MC, no profit, efficient allocation<br>
    • <b>Monopoly:</b> P > MC, highest profit, allocatively inefficient<br>
    • <b>Duopoly:</b> Between monopoly and perfect competition<br>
    • <b>Monopolistic Competition:</b> P > MC (short-run), but zero profit long-run<br>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<b>📚 Educational Simulator</b> | Learn microeconomic principles through interactive simulation<br>
Built with Streamlit | Adjust parameters and watch how firm behavior changes!
</div>
""", unsafe_allow_html=True)
