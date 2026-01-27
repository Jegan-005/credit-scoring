from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import joblib
import numpy as np
from datetime import datetime
import os
import io
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from database import (
    init_db, create_user, authenticate_user, get_user_by_username, 
    update_user_profile, database_health_check, save_credit_score_history,
    get_credit_score_history, get_credit_score_trend_data, get_score_statistics,
    save_user_financials, get_user_financials, has_financial_data,
    schedule_review, get_scheduled_reviews, get_upcoming_reviews, delete_scheduled_review
)

load_dotenv()

app = Flask(__name__)
app.secret_key = "credify_ai_secret_2024_clean"

try:
    model = joblib.load("model/credit_model.pkl")
    print("✅ AI Credit Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

def calculate_credit_metrics(age, income, existing_loans, total_emi, credit_utilization, defaults):
    if model is None:
        return 650, "Medium", income * 10, "Model not available", "warning"
    
    features = [income, age, existing_loans, total_emi, credit_utilization, defaults]
    
    try:
        credit_score = int(model.predict([features[:2]])[0])
        credit_score = max(300, min(850, credit_score))
    except:
        base_score = 500
        income_factor = min(100, income / 1000)
        age_factor = min(50, age * 2)
        loan_penalty = existing_loans * 20
        emi_penalty = min(100, total_emi / 1000)
        utilization_penalty = credit_utilization * 2
        default_penalty = defaults * 150
        
        credit_score = int(base_score + income_factor + age_factor - loan_penalty - emi_penalty - utilization_penalty - default_penalty)
        credit_score = max(300, min(850, credit_score))
    
    if credit_score >= 750:
        risk_level = "Low"
        risk_color = "success"
    elif credit_score >= 650:
        risk_level = "Medium" 
        risk_color = "warning"
    else:
        risk_level = "High"
        risk_color = "danger"
    
    base_eligibility = income * 15
    score_multiplier = credit_score / 750
    loan_penalty = existing_loans * 50000
    emi_penalty = total_emi * 12 * 2
    eligible_amount = int((base_eligibility * score_multiplier) - loan_penalty - emi_penalty)
    eligible_amount = max(0, eligible_amount)
    
    ai_explanation = generate_ai_explanation(age, income, existing_loans, total_emi, credit_utilization, defaults, credit_score, risk_level)
    
    return credit_score, risk_level, eligible_amount, ai_explanation, risk_color

def generate_ai_explanation(age, income, existing_loans, total_emi, credit_utilization, defaults, credit_score, risk_level):
    explanations = []
    
    if income >= 60000:
        explanations.append("Your high monthly income demonstrates strong financial capacity.")
    elif income >= 35000:
        explanations.append("Your moderate income shows stable earning potential.")
    else:
        explanations.append("Increasing your income could significantly improve your credit profile.")
    
    if age >= 35:
        explanations.append("Your mature age indicates financial experience and stability.")
    elif age >= 25:
        explanations.append("Your age group typically shows growing financial responsibility.")
    else:
        explanations.append("Building a longer credit history will strengthen your profile over time.")
    
    if existing_loans == 0:
        explanations.append("Having no existing loans shows good debt management.")
    elif existing_loans <= 2:
        explanations.append("Your current loan count is manageable and shows credit activity.")
    else:
        explanations.append("Multiple existing loans may impact your credit capacity.")
    
    emi_to_income_ratio = (total_emi / income) * 100 if income > 0 else 0
    if emi_to_income_ratio <= 30:
        explanations.append("Your EMI-to-income ratio is healthy.")
    elif emi_to_income_ratio <= 50:
        explanations.append("Your EMI burden is moderate but manageable.")
    else:
        explanations.append("High EMI burden may limit additional credit capacity.")
    
    if credit_utilization <= 30:
        explanations.append("Excellent credit utilization shows disciplined spending.")
    elif credit_utilization <= 60:
        explanations.append("Moderate credit utilization - consider reducing for better scores.")
    else:
        explanations.append("High credit utilization significantly impacts your score.")
    
    if defaults == 0:
        explanations.append("No past defaults demonstrate excellent payment discipline.")
    else:
        explanations.append("Past defaults negatively impact your creditworthiness.")
    
    if risk_level == "Low":
        explanations.append("The AI model predicts excellent repayment probability based on your comprehensive financial profile.")
    elif risk_level == "Medium":
        explanations.append("Your profile shows moderate risk. Focus on reducing EMI burden and credit utilization for better scores.")
    else:
        explanations.append("Focus on increasing income stability, reducing existing obligations, and maintaining payment discipline.")
    
    return " ".join(explanations)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        success, user_data, message = authenticate_user(username, password)
        
        if success:
            session["user"] = username
            session["user_id"] = user_data["id"]
            session["login_time"] = datetime.now().isoformat()
            print(f"✅ User {username} logged in successfully")
            
            if has_financial_data(username):
                return redirect(url_for("dashboard"))
            else:
                return redirect(url_for("financial_form"))
        else:
            print(f"❌ Login failed for {username}: {message}")
            return render_template("login.html", error=message)

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        email = request.form["email"].strip()

        if len(username) < 3:
            return render_template("signup.html", error="Username must be at least 3 characters long")
        
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters long")

        success, message, user_id = create_user(username, password, email)
        
        if success:
            print(f"✅ New user created: {username} (ID: {user_id})")
            return redirect(url_for("login"))
        else:
            print(f"❌ User creation failed: {message}")
            return render_template("signup.html", error=message)

    return render_template("signup.html")


@app.route("/financial-form", methods=["GET", "POST"])
def financial_form():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    
    if request.method == "POST":
        try:
            print(f"📝 Processing financial form for user: {username}")
            
            age = int(request.form["age"])
            income = int(request.form["income"])
            existing_loans = int(request.form["existing_loans"])
            total_emi = int(request.form["total_emi"])
            credit_utilization = float(request.form["credit_utilization"])
            defaults = int(request.form["defaults"])
            
            print(f"📊 Financial data: age={age}, income={income}, loans={existing_loans}, emi={total_emi}, utilization={credit_utilization}, defaults={defaults}")
            
            if age < 18 or age > 80:
                print(f"❌ Age validation failed: {age}")
                return render_template("financial_form.html", error="Age must be between 18 and 80")
            
            if income < 10000:
                print(f"❌ Income validation failed: {income}")
                return render_template("financial_form.html", error="Minimum income requirement: ₹10,000")
            
            if existing_loans < 0:
                print(f"❌ Loans validation failed: {existing_loans}")
                return render_template("financial_form.html", error="Existing loans cannot be negative")
            
            if total_emi < 0:
                print(f"❌ EMI validation failed: {total_emi}")
                return render_template("financial_form.html", error="Total EMI cannot be negative")
            
            if credit_utilization < 0 or credit_utilization > 100:
                print(f"❌ Credit utilization validation failed: {credit_utilization}")
                return render_template("financial_form.html", error="Credit utilization must be between 0 and 100")
            
            if defaults < 0:
                print(f"❌ Defaults validation failed: {defaults}")
                return render_template("financial_form.html", error="Number of defaults cannot be negative")
            
            print(f"✅ All validations passed, saving financial data...")
            success, message = save_user_financials(username, age, income, existing_loans, total_emi, credit_utilization, defaults)
            
            if success:
                print(f"✅ Financial data saved successfully for {username}")
                return redirect(url_for("dashboard"))
            else:
                print(f"❌ Failed to save financial data for {username}: {message}")
                return render_template("financial_form.html", error=f"Failed to save data: {message}")
                
        except ValueError as e:
            print(f"❌ ValueError in financial form: {e}")
            return render_template("financial_form.html", error="Please enter valid numbers for all fields")
        except Exception as e:
            print(f"❌ Unexpected error in financial form: {e}")
            import traceback
            traceback.print_exc()
            return render_template("financial_form.html", error="An unexpected error occurred. Please try again.")
    
    # GET request - load existing data if available
    financial_data = get_user_financials(username)
    print(f"📖 Loading financial form for {username}, existing data: {financial_data is not None}")
    return render_template("financial_form.html", data=financial_data)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    print(f"📊 Loading dashboard for user: {username}")
    
    try:
        financial_data = get_user_financials(username)
        if not financial_data:
            print(f"❌ No financial data found for {username}, redirecting to financial form")
            return redirect(url_for("financial_form"))

        print(f"✅ Financial data loaded for {username}: {financial_data}")

        age = financial_data["age"]
        income = financial_data["income"]
        existing_loans = financial_data["existing_loans"]
        total_emi = financial_data["total_emi"]
        credit_utilization = financial_data["credit_utilization"]
        defaults = financial_data["defaults"]

        print(f"🧮 Calculating credit metrics...")
        credit_score, risk_level, eligible_amount, ai_explanation, risk_color = calculate_credit_metrics(
            age, income, existing_loans, total_emi, credit_utilization, defaults
        )
        print(f"✅ Credit metrics calculated: score={credit_score}, risk={risk_level}")

        try:
            history_success, history_message = save_credit_score_history(
                username, credit_score, risk_level, eligible_amount
            )
            if history_success:
                print(f"✅ Credit score history saved for {username}")
            else:
                print(f"⚠️ Failed to save credit history: {history_message}")
        except Exception as e:
            print(f"⚠️ Credit history error: {e}")

        score_history = get_credit_score_history(username, limit=10)
        trend_data = get_credit_score_trend_data(username, days=30)
        score_stats = get_score_statistics(username)

        monthly_emi_capacity = int(income * 0.4)
        
        print(f"✅ Dashboard data prepared successfully for {username}")
        
        return render_template(
            "dashboard.html",
            user=username,
            credit_score=credit_score,
            risk_level=risk_level,
            risk_color=risk_color,
            eligible_amount=eligible_amount,
            ai_explanation=ai_explanation,
            monthly_emi_capacity=monthly_emi_capacity,
            credit_utilization=credit_utilization,
            income=income,
            age=age,
            existing_loans=existing_loans,
            total_emi=total_emi,
            defaults=defaults,
            score_history=score_history,
            trend_data=trend_data,
            score_stats=score_stats
        )
        
    except Exception as e:
        print(f"❌ Dashboard error for {username}: {e}")
        import traceback
        traceback.print_exc()
        return render_template("dashboard.html", 
                             user=username, 
                             error="An error occurred while loading your dashboard. Please try again.",
                             credit_score=650,
                             risk_level="Medium",
                             risk_color="warning",
                             eligible_amount=500000,
                             ai_explanation="Unable to calculate at this time.",
                             monthly_emi_capacity=20000,
                             credit_utilization=30.0,
                             income=50000,
                             age=30,
                             existing_loans=0,
                             total_emi=0,
                             defaults=0,
                             score_history=[],
                             trend_data={'dates': [], 'scores': []},
                             score_stats={'min_score': 0, 'max_score': 0, 'avg_score': 0, 'total_records': 0})

@app.route("/download-report")
def download_report():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    
    user_data = get_user_by_username(username)
    if not user_data:
        return jsonify({"error": "User data not found"}), 404
    
    financial_data = get_user_financials(username)
    if not financial_data:
        return jsonify({"error": "Financial data not found. Please complete your financial profile first."}), 404
    
    age = financial_data["age"]
    income = financial_data["income"]
    existing_loans = financial_data["existing_loans"]
    total_emi = financial_data["total_emi"]
    credit_utilization = financial_data["credit_utilization"]
    defaults = financial_data["defaults"]
    
    credit_score, risk_level, eligible_amount, ai_explanation, risk_color = calculate_credit_metrics(
        age, income, existing_loans, total_emi, credit_utilization, defaults
    )
    
    monthly_emi_capacity = int(income * 0.4)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#00e5ff')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor('#2c5364')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#2c5364')
    )
    
    elements.append(Paragraph("CredX AI", title_style))
    elements.append(Paragraph("Credit Score Analysis Report", subtitle_style))
    elements.append(Paragraph(f"Username: {username}", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("Credit Score Summary", heading_style))
    
    summary_data = [
        ['Credit Score', f"{credit_score}/850"],
        ['Risk Level', risk_level],
        ['Loan Eligibility', f"₹{eligible_amount:,}"],
        ['Monthly EMI Capacity', f"₹{monthly_emi_capacity:,}"],
        ['Credit Utilization', f"{credit_utilization:.1f}%"]
    ]
    
    risk_colors = {
        'Low': colors.green,
        'Medium': colors.orange,
        'High': colors.red
    }
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#00e5ff')),
        ('TEXTCOLOR', (1, 1), (1, 1), risk_colors.get(risk_level, colors.black)),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (1, 0), 16),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#00e5ff'))
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("Financial Profile", heading_style))
    financial_profile_data = [
        ['Age', f"{age} years"],
        ['Monthly Income', f"₹{income:,}"],
        ['Existing Loans', str(existing_loans)],
        ['Total EMI', f"₹{total_emi:,}"],
        ['Past Defaults', 'Yes' if defaults == 1 else 'No']
    ]
    
    financial_table = Table(financial_profile_data, colWidths=[2.5*inch, 2.5*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(financial_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("AI Analysis & Recommendations", heading_style))
    elements.append(Paragraph(ai_explanation, styles['Normal']))
    elements.append(Spacer(1, 40))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#00e5ff'),
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("Generated by CredX AI", footer_style))
    
    doc.build(elements)
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"CredX_Credit_Analysis_Report_{username}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mimetype='application/pdf'
    )

@app.route("/schedule-review", methods=["GET", "POST"])
def schedule_review_route():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    
    if request.method == "POST":
        try:
            review_date = request.form.get("review_date", "").strip()
            note = request.form.get("note", "").strip()
            
            if not review_date:
                return jsonify({"success": False, "message": "Review date is required"}), 400
            
            from datetime import datetime, date
            try:
                review_date_obj = datetime.strptime(review_date, '%Y-%m-%d').date()
                if review_date_obj <= date.today():
                    return jsonify({"success": False, "message": "Review date must be in the future"}), 400
            except ValueError:
                return jsonify({"success": False, "message": "Invalid date format"}), 400
            
            success, message = schedule_review(username, review_date, note if note else None)
            
            if success:
                return jsonify({"success": True, "message": "Your credit review has been scheduled successfully!"})
            else:
                return jsonify({"success": False, "message": f"Failed to schedule review: {message}"}), 500
                
        except Exception as e:
            print(f"❌ Schedule review error: {e}")
            return jsonify({"success": False, "message": "An unexpected error occurred"}), 500
    
    scheduled_reviews = get_scheduled_reviews(username, limit=10)
    upcoming_reviews = get_upcoming_reviews(username, days_ahead=30)
    
    return render_template("schedule_review.html", 
                         scheduled_reviews=scheduled_reviews,
                         upcoming_reviews=upcoming_reviews)

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    
    user_data = get_user_by_username(username)
    if not user_data:
        print(f"❌ User data not found for {username}")
        session.clear()
        return redirect(url_for("login"))
    
    financial_data = get_user_financials(username)
    
    credit_score = 0
    risk_level = "Unknown"
    risk_color = "secondary"
    
    if financial_data:
        credit_score, risk_level, _, _, risk_color = calculate_credit_metrics(
            financial_data["age"], financial_data["income"], financial_data["existing_loans"],
            financial_data["total_emi"], financial_data["credit_utilization"], financial_data["defaults"]
        )
    
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    
    return render_template(
        "profile.html",
        username=username,
        data=user_data,
        financial_data=financial_data,
        credit_score=credit_score,
        risk_level=risk_level,
        risk_color=risk_color,
        success_message=success_message,
        error_message=error_message
    )

@app.route("/update-profile", methods=["POST"])
def update_profile():
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    
    try:
        email = request.form.get("email", "").strip()
        
        if not email:
            return redirect(url_for("profile", error_message="Email is required"))
        
        if "@" not in email or "." not in email:
            return redirect(url_for("profile", error_message="Please enter a valid email address"))
        
        success, message = update_user_profile(username, email)
        
        if success:
            print(f"✅ Profile updated successfully for {username}")
            return redirect(url_for("profile", success_message="Profile updated successfully!"))
        else:
            print(f"❌ Profile update failed for {username}: {message}")
            return redirect(url_for("profile", error_message=f"Update failed: {message}"))
        
    except Exception as e:
        print(f"❌ Profile update error: {e}")
        return redirect(url_for("profile", error_message="An unexpected error occurred. Please try again."))

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"reply": "Please login to use the AI assistant."})

    username = session["user"]
    
    financial_data = get_user_financials(username)
    if not financial_data:
        return jsonify({"reply": "Please complete your financial profile first to get personalized assistance."})

    age = financial_data["age"]
    income = financial_data["income"]
    existing_loans = financial_data["existing_loans"]
    total_emi = financial_data["total_emi"]
    credit_utilization = financial_data["credit_utilization"]
    defaults = financial_data["defaults"]
    
    credit_score, risk_level, eligible_amount, _, _ = calculate_credit_metrics(
        age, income, existing_loans, total_emi, credit_utilization, defaults
    )

    user_message = request.json["message"].lower()

    if any(word in user_message for word in ["credit score", "score", "rating"]):
        reply = f"Your AI-predicted credit score is {credit_score}/850. This score is calculated using advanced machine learning algorithms that analyze your comprehensive financial profile including income (₹{income:,}), age ({age} years), existing loans ({existing_loans}), and credit utilization ({credit_utilization}%)."

    elif any(word in user_message for word in ["risk", "risk level", "danger"]):
        if risk_level == "Low":
            reply = f"Excellent! Your risk level is {risk_level}. This means you have a high probability of loan repayment and qualify for premium financial products with better interest rates."
        elif risk_level == "Medium":
            reply = f"Your risk level is {risk_level}. You're in a stable category but can improve by optimizing your debt-to-income ratio and credit utilization."
        else:
            reply = f"Your risk level is {risk_level}. Focus on income stability, reducing existing loan burden (currently {existing_loans} loans), and maintaining payment discipline."

    elif any(word in user_message for word in ["improve", "increase", "better", "tips"]):
        tips = []
        if income < 50000:
            tips.append("Increase monthly income above ₹50,000")
        if credit_utilization > 30:
            tips.append(f"Reduce credit utilization from {credit_utilization}% to below 30%")
        if existing_loans > 2:
            tips.append("Consider consolidating multiple loans")
        if total_emi > income * 0.4:
            tips.append("Reduce EMI burden to below 40% of income")
        if defaults > 0:
            tips.append("Maintain consistent payment history going forward")
        
        if not tips:
            tips = ["Maintain current excellent financial discipline", "Consider diversifying credit portfolio", "Explore investment opportunities"]
        
        reply = f"Here are personalized AI recommendations to improve your credit score: {' • '.join(tips)}"

    else:
        reply = "I'm your AI Financial Assistant! Ask me about: • Credit Score • Risk Level • Loan Eligibility • EMI Analysis • Credit Utilization • Improvement Tips • Interest Rates • Financial Profile"

    return jsonify({"reply": reply})

@app.route("/logout")
def logout():
    username = session.get("user", "Unknown")
    session.clear()
    print(f"✅ User {username} logged out")
    return redirect(url_for("landing"))

@app.route("/api/credit-trend/<username>")
def get_credit_trend_api(username):
    if "user" not in session or session["user"] != username:
        return jsonify({"error": "Unauthorized"}), 401
    
    days = request.args.get('days', 30, type=int)
    trend_data = get_credit_score_trend_data(username, days)
    
    return jsonify(trend_data)

@app.route("/api/credit-history/<username>")
def get_credit_history_api(username):
    if "user" not in session or session["user"] != username:
        return jsonify({"error": "Unauthorized"}), 401
    
    limit = request.args.get('limit', 10, type=int)
    history = get_credit_score_history(username, limit)
    
    return jsonify({"history": history})

@app.route("/api/credit-check", methods=["POST"])
def api_credit_check():
    try:
        data = request.json
        age = data.get("age")
        income = data.get("income")
        existing_loans = data.get("existing_loans", 0)
        total_emi = data.get("total_emi", 0)
        credit_utilization = data.get("credit_utilization", 30)
        defaults = data.get("defaults", 0)
        
        if not age or not income:
            return jsonify({"error": "Age and income required"}), 400
        
        age = int(age)
        income = int(income)
        existing_loans = int(existing_loans)
        total_emi = int(total_emi)
        credit_utilization = float(credit_utilization)
        defaults = int(defaults)
        
        if age < 18 or age > 80:
            return jsonify({"error": "Age must be between 18 and 80"}), 400
        
        if income < 10000:
            return jsonify({"error": "Minimum income requirement: ₹10,000"}), 400
        
        if credit_utilization < 0 or credit_utilization > 100:
            return jsonify({"error": "Credit utilization must be between 0 and 100"}), 400
        
        credit_score, risk_level, eligible_amount, explanation, _ = calculate_credit_metrics(
            age, income, existing_loans, total_emi, credit_utilization, defaults
        )
        
        return jsonify({
            "credit_score": credit_score,
            "risk_level": risk_level,
            "eligible_amount": eligible_amount,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        })
        
    except ValueError:
        return jsonify({"error": "Invalid input data"}), 400
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/delete-review/<int:review_id>", methods=["DELETE"])
def delete_review_api(review_id):
    if "user" not in session:
        return jsonify({"success": False, "message": "Authentication required"}), 401
    
    username = session["user"]
    
    try:
        success, message = delete_scheduled_review(username, review_id)
        return jsonify({"success": success, "message": message})
    except Exception as e:
        print(f"❌ Delete review error: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred"}), 500

@app.route("/api/health")
def health_check():
    db_health = database_health_check()
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None,
        "database": db_health
    })

@app.route("/api/stats")
def get_stats():
    if "user" not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    db_health = database_health_check()
    
    return jsonify({
        "total_users": db_health.get("user_count", 0),
        "database_size_kb": db_health.get("database_size_kb", 0),
        "model_status": "loaded" if model else "not_loaded",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

if __name__ == "__main__":
    print("🚀 Starting CredX AI Credit Scoring System...")
    
    try:
        init_db()
        
        health = database_health_check()
        print(f"📊 Database Status: {health['status']}")
        print(f"👥 Total Users: {health.get('user_count', 0)}")
        print(f"💾 Database Size: {health.get('database_size_kb', 0)} KB")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    print("🌐 Application URLs:")
    print("   • Main App: http://localhost:5000")
    print("   • Health Check: http://localhost:5000/api/health")
    print("   • API Stats: http://localhost:5000/api/stats")
    
    print("✅ Email system removed - Clean and stable version")
    
    app.run(debug=True, host="0.0.0.0", port=5000)