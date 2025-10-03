from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any

def generate_health_report_pdf(prediction_data: Dict[str, Any], user_info: Dict[str, Any]) -> BytesIO:
    """Generate a comprehensive personalized health report PDF"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Extract comprehensive data for detailed analysis
    input_data = prediction_data.get('input_data', {})
    comprehensive_analysis = prediction_data.get('comprehensive_analysis', {})
    diabetes_risk = prediction_data.get('diabetes_risk', 0) * 100
    hypertension_risk = prediction_data.get('hypertension_risk', 0) * 100
    metabolic_score = prediction_data.get('metabolic_health_score', 0)
    cardio_score = prediction_data.get('cardiovascular_health_score', 0)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    # Title
    elements.append(Paragraph("PreventiX Health Risk Assessment Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report Info
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    elements.append(Paragraph(f"<b>Report Generated:</b> {report_date}", normal_style))
    elements.append(Paragraph(f"<b>Patient Name:</b> {user_info.get('name', 'N/A')}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Personalized Health Profile
    elements.append(Paragraph("Personalized Health Profile", heading_style))
    
    # Extract key health metrics
    age = input_data.get('age', 'N/A')
    gender = "Male" if input_data.get('gender', 0) == 1 else "Female"
    bmi = input_data.get('bmi', 'N/A')
    blood_pressure = input_data.get('blood_pressure', 'N/A')
    glucose = input_data.get('glucose_level', 'N/A')
    cholesterol = input_data.get('cholesterol_level', 'N/A')
    physical_activity = input_data.get('physical_activity', 'N/A')
    smoking_status = input_data.get('smoking_status', 0)
    smoking_text = ["Never", "Former", "Current"][int(smoking_status)] if smoking_status in [0, 1, 2] else "Unknown"
    stress_level = input_data.get('stress_level', 5)
    sleep_hours = input_data.get('sleep_hours', 7)
    
    profile_data = [
        ['Health Metric', 'Your Value', 'Normal Range', 'Status'],
        ['Age', f"{age} years", 'N/A', 'Baseline'],
        ['Gender', gender, 'N/A', 'Baseline'],
        ['BMI', f"{bmi:.1f}", '18.5-24.9', get_bmi_status(bmi)],
        ['Blood Pressure', f"{blood_pressure} mmHg", '<120/80', get_bp_status(blood_pressure)],
        ['Glucose Level', f"{glucose} mg/dL", '70-100', get_glucose_status(glucose)],
        ['Cholesterol', f"{cholesterol} mg/dL", '<200', get_cholesterol_status(cholesterol)],
        ['Physical Activity', f"{physical_activity}/10", '7-10', get_activity_status(physical_activity)],
        ['Smoking Status', smoking_text, 'Never', get_smoking_status(smoking_status)]
    ]
    
    profile_table = Table(profile_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.5*inch])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(profile_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Risk Summary Section
    elements.append(Paragraph("Comprehensive Risk Analysis", heading_style))
    
    # Detailed risk analysis with personalized insights
    risk_data = [
        ['Risk Category', 'Your Risk Level', 'Population Average', 'Risk Status', 'Priority'],
        ['Diabetes', f"{diabetes_risk:.1f}%", '8.5%', get_risk_status(diabetes_risk), get_priority_level(diabetes_risk)],
        ['Hypertension', f"{hypertension_risk:.1f}%", '32%', get_risk_status(hypertension_risk), get_priority_level(hypertension_risk)]
    ]
    
    risk_table = Table(risk_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.8*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    risk_table = Table(risk_data, colWidths=[1.4*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.0*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(risk_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed Risk Factors Analysis
    elements.append(Paragraph("Detailed Risk Factors Analysis", heading_style))
    
    # Diabetes Risk Factors
    elements.append(Paragraph("Diabetes Risk Factors:", subheading_style))
    diabetes_factors = comprehensive_analysis.get('diabetes_risk_factors', {})
    
    # Critical concerns
    critical_concerns = diabetes_factors.get('critical_concerns', [])
    if critical_concerns:
        elements.append(Paragraph("🚨 <b>Critical Concerns:</b>", normal_style))
        for concern in critical_concerns[:3]:
            elements.append(Paragraph(f"• <b>{concern.get('factor', 'Unknown')}:</b> {concern.get('explanation', 'No explanation')}", normal_style))
            elements.append(Paragraph(f"  <i>Recommendation:</i> {concern.get('recommendation', 'Consult healthcare provider')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Risk factors
    risk_factors = diabetes_factors.get('risk_factors', [])
    if risk_factors:
        elements.append(Paragraph("⚠️ <b>Risk Factors:</b>", normal_style))
        for factor in risk_factors[:3]:
            elements.append(Paragraph(f"• <b>{factor.get('factor', 'Unknown')}:</b> {factor.get('explanation', 'No explanation')}", normal_style))
            elements.append(Paragraph(f"  <i>Recommendation:</i> {factor.get('recommendation', 'Focus on lifestyle improvements')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Protective factors
    protective_factors = diabetes_factors.get('protective_factors', [])
    if protective_factors:
        elements.append(Paragraph("✅ <b>Protective Factors:</b>", normal_style))
        for factor in protective_factors[:2]:
            elements.append(Paragraph(f"• <b>{factor.get('factor', 'Unknown')}:</b> {factor.get('explanation', 'No explanation')}", normal_style))
            elements.append(Paragraph(f"  <i>Continue:</i> {factor.get('recommendation', 'Maintain current habits')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Hypertension Risk Factors
    elements.append(Paragraph("Hypertension Risk Factors:", subheading_style))
    hypertension_factors = comprehensive_analysis.get('hypertension_risk_factors', {})
    
    # Critical concerns
    htn_critical = hypertension_factors.get('critical_concerns', [])
    if htn_critical:
        elements.append(Paragraph("🚨 <b>Critical Concerns:</b>", normal_style))
        for concern in htn_critical[:3]:
            elements.append(Paragraph(f"• <b>{concern.get('factor', 'Unknown')}:</b> {concern.get('explanation', 'No explanation')}", normal_style))
            elements.append(Paragraph(f"  <i>Recommendation:</i> {concern.get('recommendation', 'Consult healthcare provider')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Risk factors
    htn_risk = hypertension_factors.get('risk_factors', [])
    if htn_risk:
        elements.append(Paragraph("⚠️ <b>Risk Factors:</b>", normal_style))
        for factor in htn_risk[:3]:
            elements.append(Paragraph(f"• <b>{factor.get('factor', 'Unknown')}:</b> {factor.get('explanation', 'No explanation')}", normal_style))
            elements.append(Paragraph(f"  <i>Recommendation:</i> {factor.get('recommendation', 'Focus on blood pressure management')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Protective factors
    htn_protective = hypertension_factors.get('protective_factors', [])
    if htn_protective:
        elements.append(Paragraph("✅ <b>Protective Factors:</b>", normal_style))
        for factor in htn_protective[:2]:
            elements.append(Paragraph(f"• <b>{factor.get('factor', 'Unknown')}:</b> {factor.get('explanation', 'No explanation')}", normal_style))
            elements.append(Paragraph(f"  <i>Continue:</i> {factor.get('recommendation', 'Maintain current habits')}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    elements.append(PageBreak())
    
    # Health Scores
    elements.append(Paragraph("Comprehensive Health Scores", heading_style))
    
    metabolic_score = prediction_data.get('metabolic_health_score', 0)
    cardio_score = prediction_data.get('cardiovascular_health_score', 0)
    
    # Enhanced health scores with detailed breakdown
    score_data = [
        ['Health Metric', 'Your Score', 'Optimal Range', 'Status', 'Action Required'],
        ['Metabolic Health', f"{metabolic_score:.1f}/100", '85-100', get_score_interpretation(metabolic_score), get_action_required(metabolic_score)],
        ['Cardiovascular Health', f"{cardio_score:.1f}/100", '85-100', get_score_interpretation(cardio_score), get_action_required(cardio_score)]
    ]
    
    score_table = Table(score_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch, 1.6*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed Health Analysis
    elements.append(Paragraph("Detailed Health Analysis", heading_style))
    
    # Metabolic Health Analysis
    metabolic_analysis = comprehensive_analysis.get('metabolic_health_analysis', {})
    if metabolic_analysis:
        elements.append(Paragraph("Metabolic Health Analysis:", subheading_style))
        
        concerns = metabolic_analysis.get('concerns', [])
        if concerns:
            elements.append(Paragraph("⚠️ <b>Areas of Concern:</b>", normal_style))
            for concern in concerns[:3]:
                elements.append(Paragraph(f"• {concern}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        strengths = metabolic_analysis.get('strengths', [])
        if strengths:
            elements.append(Paragraph("✅ <b>Strengths:</b>", normal_style))
            for strength in strengths[:3]:
                elements.append(Paragraph(f"• {strength}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        recommendations = metabolic_analysis.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("💡 <b>Recommendations:</b>", normal_style))
            for rec in recommendations[:4]:
                elements.append(Paragraph(f"• {rec}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    # Cardiovascular Health Analysis
    cardio_analysis = comprehensive_analysis.get('cardiovascular_health_analysis', {})
    if cardio_analysis:
        elements.append(Paragraph("Cardiovascular Health Analysis:", subheading_style))
        
        concerns = cardio_analysis.get('concerns', [])
        if concerns:
            elements.append(Paragraph("⚠️ <b>Areas of Concern:</b>", normal_style))
            for concern in concerns[:3]:
                elements.append(Paragraph(f"• {concern}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        strengths = cardio_analysis.get('strengths', [])
        if strengths:
            elements.append(Paragraph("✅ <b>Strengths:</b>", normal_style))
            for strength in strengths[:3]:
                elements.append(Paragraph(f"• {strength}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        recommendations = cardio_analysis.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("💡 <b>Recommendations:</b>", normal_style))
            for rec in recommendations[:4]:
                elements.append(Paragraph(f"• {rec}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    
    elements.append(PageBreak())
    
    # Top Risk Factors
    elements.append(Paragraph("Top Risk Factors", heading_style))
    elements.append(Paragraph("Diabetes Risk Factors:", subheading_style))
    
    diabetes_factors = prediction_data.get('top_diabetes_factors', [])[:3]
    for i, factor in enumerate(diabetes_factors, 1):
        factor_name = factor.get('feature', 'Unknown').replace('_', ' ').title()
        factor_value = factor.get('value', 'N/A')
        elements.append(Paragraph(f"{i}. <b>{factor_name}:</b> {factor_value}", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Hypertension Risk Factors:", subheading_style))
    
    hypertension_factors = prediction_data.get('top_hypertension_factors', [])[:3]
    for i, factor in enumerate(hypertension_factors, 1):
        factor_name = factor.get('feature', 'Unknown').replace('_', ' ').title()
        factor_value = factor.get('value', 'N/A')
        elements.append(Paragraph(f"{i}. <b>{factor_name}:</b> {factor_value}", normal_style))
    
    elements.append(PageBreak())
    
    # Comprehensive Personalized Recommendations
    elements.append(Paragraph("Comprehensive Personalized Recommendations", heading_style))
    
    # Nutrition Recommendations
    elements.append(Paragraph("🍎 Nutrition & Diet Recommendations:", subheading_style))
    nutrition_recs = prediction_data.get('nutrition_recommendations', {}).get('primary', [])
    if nutrition_recs:
        for i, rec in enumerate(nutrition_recs[:6], 1):
            elements.append(Paragraph(f"{i}. {rec}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        # Fallback nutrition recommendations based on health data
        elements.append(Paragraph("Based on your health profile:", normal_style))
        if diabetes_risk > 30:
            elements.append(Paragraph("• Focus on low-glycemic index foods to manage blood sugar", normal_style))
            elements.append(Paragraph("• Limit refined carbohydrates and added sugars", normal_style))
            elements.append(Paragraph("• Increase fiber intake with vegetables and whole grains", normal_style))
        if hypertension_risk > 30:
            elements.append(Paragraph("• Reduce sodium intake to less than 2,300mg per day", normal_style))
            elements.append(Paragraph("• Increase potassium-rich foods like bananas and leafy greens", normal_style))
            elements.append(Paragraph("• Limit processed foods and restaurant meals", normal_style))
        if bmi > 25:
            elements.append(Paragraph("• Create a moderate calorie deficit for sustainable weight loss", normal_style))
            elements.append(Paragraph("• Focus on portion control and mindful eating", normal_style))
    
    # Fitness Recommendations
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("🏃‍♂️ Fitness & Exercise Recommendations:", subheading_style))
    fitness_recs = prediction_data.get('fitness_recommendations', {}).get('primary', [])
    if fitness_recs:
        for i, rec in enumerate(fitness_recs[:6], 1):
            elements.append(Paragraph(f"{i}. {rec}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        # Fallback fitness recommendations
        elements.append(Paragraph("Based on your health profile:", normal_style))
        if diabetes_risk > 30:
            elements.append(Paragraph("• Aim for 150 minutes of moderate aerobic exercise weekly", normal_style))
            elements.append(Paragraph("• Include resistance training 2-3 times per week", normal_style))
            elements.append(Paragraph("• Focus on activities that improve insulin sensitivity", normal_style))
        if hypertension_risk > 30:
            elements.append(Paragraph("• Engage in regular cardiovascular exercise", normal_style))
            elements.append(Paragraph("• Include stress-reducing activities like yoga or meditation", normal_style))
            elements.append(Paragraph("• Start with low-impact activities if you're new to exercise", normal_style))
        if physical_activity < 5:
            elements.append(Paragraph("• Start with 10-15 minutes of daily activity and gradually increase", normal_style))
            elements.append(Paragraph("• Find activities you enjoy to maintain consistency", normal_style))
    
    # Lifestyle Recommendations
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("🌱 Lifestyle & Wellness Recommendations:", subheading_style))
    lifestyle_recs = prediction_data.get('lifestyle_recommendations', [])
    if lifestyle_recs:
        for i, rec in enumerate(lifestyle_recs[:6], 1):
            elements.append(Paragraph(f"{i}. {rec}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        # Fallback lifestyle recommendations
        elements.append(Paragraph("Based on your health profile:", normal_style))
        if smoking_status == 2:  # Current smoker
            elements.append(Paragraph("• Prioritize smoking cessation - this is the most important change", normal_style))
            elements.append(Paragraph("• Consider nicotine replacement therapy or other cessation aids", normal_style))
            elements.append(Paragraph("• Seek support from healthcare providers or cessation programs", normal_style))
        if stress_level and stress_level > 7:
            elements.append(Paragraph("• Implement stress management techniques like meditation or deep breathing", normal_style))
            elements.append(Paragraph("• Ensure adequate sleep (7-9 hours per night)", normal_style))
            elements.append(Paragraph("• Consider professional help for stress management if needed", normal_style))
        if sleep_hours and sleep_hours < 6:
            elements.append(Paragraph("• Prioritize sleep hygiene and consistent sleep schedule", normal_style))
            elements.append(Paragraph("• Create a relaxing bedtime routine", normal_style))
            elements.append(Paragraph("• Limit screen time before bed", normal_style))
    
    # Personalized Action Plan
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("📋 Your Personalized 30-Day Action Plan", heading_style))
    
    # Week 1-2
    elements.append(Paragraph("Week 1-2: Foundation Building", subheading_style))
    elements.append(Paragraph("• Start with small, sustainable changes", normal_style))
    elements.append(Paragraph("• Focus on one major habit at a time", normal_style))
    elements.append(Paragraph("• Track your progress daily", normal_style))
    if diabetes_risk > 30:
        elements.append(Paragraph("• Begin monitoring blood sugar if recommended by your doctor", normal_style))
    if hypertension_risk > 30:
        elements.append(Paragraph("• Start checking blood pressure regularly", normal_style))
    
    # Week 3-4
    elements.append(Paragraph("Week 3-4: Habit Reinforcement", subheading_style))
    elements.append(Paragraph("• Increase intensity of your chosen activities", normal_style))
    elements.append(Paragraph("• Add variety to prevent boredom", normal_style))
    elements.append(Paragraph("• Celebrate small victories", normal_style))
    elements.append(Paragraph("• Plan for potential obstacles", normal_style))
    
    # Long-term goals
    elements.append(Paragraph("Long-term Goals (3-6 months):", subheading_style))
    if diabetes_risk > 30:
        elements.append(Paragraph("• Achieve and maintain target blood sugar levels", normal_style))
        elements.append(Paragraph("• Lose 5-10% of body weight if overweight", normal_style))
    if hypertension_risk > 30:
        elements.append(Paragraph("• Achieve blood pressure below 130/80 mmHg", normal_style))
        elements.append(Paragraph("• Reduce sodium intake to less than 1,500mg daily", normal_style))
    elements.append(Paragraph("• Establish consistent exercise routine", normal_style))
    elements.append(Paragraph("• Regular health monitoring and checkups", normal_style))
    
    # Monitoring and Follow-up Recommendations
    elements.append(PageBreak())
    elements.append(Paragraph("📊 Health Monitoring & Follow-up Recommendations", heading_style))
    
    # Personalized monitoring schedule
    elements.append(Paragraph("Your Personalized Monitoring Schedule:", subheading_style))
    
    # Daily monitoring
    elements.append(Paragraph("Daily Monitoring:", normal_style))
    if diabetes_risk > 30:
        elements.append(Paragraph("• Blood glucose levels (if recommended by doctor)", normal_style))
    if hypertension_risk > 30:
        elements.append(Paragraph("• Blood pressure readings", normal_style))
    elements.append(Paragraph("• Physical activity tracking", normal_style))
    elements.append(Paragraph("• Sleep quality and duration", normal_style))
    elements.append(Paragraph("• Stress levels and mood", normal_style))
    
    # Weekly monitoring
    elements.append(Paragraph("Weekly Monitoring:", normal_style))
    elements.append(Paragraph("• Weight tracking", normal_style))
    elements.append(Paragraph("• Exercise intensity and duration", normal_style))
    elements.append(Paragraph("• Nutrition adherence", normal_style))
    if smoking_status == 2:
        elements.append(Paragraph("• Smoking cessation progress", normal_style))
    
    # Monthly monitoring
    elements.append(Paragraph("Monthly Monitoring:", normal_style))
    elements.append(Paragraph("• Overall health assessment", normal_style))
    elements.append(Paragraph("• Progress toward goals", normal_style))
    elements.append(Paragraph("• Adjustment of strategies if needed", normal_style))
    
    # Healthcare provider visits
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Healthcare Provider Visits:", subheading_style))
    
    if diabetes_risk > 30 or hypertension_risk > 30:
        elements.append(Paragraph("• Schedule appointment within 2-4 weeks", normal_style))
        elements.append(Paragraph("• Bring this report to your healthcare provider", normal_style))
        elements.append(Paragraph("• Discuss specific risk factors and management strategies", normal_style))
    else:
        elements.append(Paragraph("• Schedule annual wellness visit", normal_style))
        elements.append(Paragraph("• Continue regular health monitoring", normal_style))
        elements.append(Paragraph("• Maintain preventive health measures", normal_style))
    
    # Emergency situations
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("When to Seek Immediate Medical Attention:", subheading_style))
    elements.append(Paragraph("• Severe chest pain or pressure", normal_style))
    elements.append(Paragraph("• Difficulty breathing or shortness of breath", normal_style))
    elements.append(Paragraph("• Severe headache with vision changes", normal_style))
    elements.append(Paragraph("• Loss of consciousness or severe dizziness", normal_style))
    elements.append(Paragraph("• Any other severe or sudden symptoms", normal_style))
    
    # Personalized Insights
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("🎯 Your Personalized Health Insights", heading_style))
    
    insights = prediction_data.get('personalized_insights', [])
    if insights:
        for insight in insights[:8]:
            elements.append(Paragraph(f"• {insight}", normal_style))
            elements.append(Spacer(1, 0.1*inch))
    else:
        # Generate personalized insights based on health data
        elements.append(Paragraph("Based on your health assessment:", normal_style))
        
        if diabetes_risk > 50:
            elements.append(Paragraph("• Your diabetes risk is significantly elevated and requires immediate attention", normal_style))
            elements.append(Paragraph("• Focus on blood sugar management and weight control", normal_style))
        elif diabetes_risk > 20:
            elements.append(Paragraph("• You have moderate diabetes risk that can be managed with lifestyle changes", normal_style))
            elements.append(Paragraph("• Early intervention can prevent progression to diabetes", normal_style))
        else:
            elements.append(Paragraph("• Your diabetes risk is low - continue your healthy habits", normal_style))
        
        if hypertension_risk > 50:
            elements.append(Paragraph("• Your blood pressure risk is high and needs medical attention", normal_style))
            elements.append(Paragraph("• Focus on sodium reduction and stress management", normal_style))
        elif hypertension_risk > 20:
            elements.append(Paragraph("• You have moderate blood pressure risk that can be improved", normal_style))
            elements.append(Paragraph("• Regular exercise and diet modifications can help", normal_style))
        else:
            elements.append(Paragraph("• Your cardiovascular risk is low - maintain your healthy lifestyle", normal_style))
        
        if bmi > 30:
            elements.append(Paragraph("• Weight management should be a primary focus", normal_style))
            elements.append(Paragraph("• Even modest weight loss can significantly improve health outcomes", normal_style))
        elif bmi > 25:
            elements.append(Paragraph("• Consider weight management to optimize your health", normal_style))
            elements.append(Paragraph("• Small changes can make a big difference", normal_style))
        else:
            elements.append(Paragraph("• Your weight is in a healthy range - continue to maintain it", normal_style))
    
    # Disclaimer
    elements.append(Spacer(1, 0.4*inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_JUSTIFY
    )
    
    disclaimer_text = """
    <b>Medical Disclaimer:</b> This report is generated by an AI-powered health risk assessment tool and is intended 
    for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any questions you may have 
    regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of 
    something you have read in this report.
    """
    
    elements.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def get_score_interpretation(score: float) -> str:
    """Interpret health score"""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Fair"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Critical - Seek Medical Attention"

def get_bmi_status(bmi: float) -> str:
    """Get BMI status"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_bp_status(bp: float) -> str:
    """Get blood pressure status"""
    if bp < 120:
        return "Normal"
    elif bp < 130:
        return "Elevated"
    elif bp < 140:
        return "Stage 1 Hypertension"
    else:
        return "Stage 2 Hypertension"

def get_glucose_status(glucose: float) -> str:
    """Get glucose status"""
    if glucose < 100:
        return "Normal"
    elif glucose < 126:
        return "Pre-diabetic"
    else:
        return "Diabetic Range"

def get_cholesterol_status(cholesterol: float) -> str:
    """Get cholesterol status"""
    if cholesterol < 200:
        return "Desirable"
    elif cholesterol < 240:
        return "Borderline High"
    else:
        return "High"

def get_activity_status(activity: float) -> str:
    """Get physical activity status"""
    if activity >= 7:
        return "Active"
    elif activity >= 4:
        return "Moderately Active"
    else:
        return "Sedentary"

def get_smoking_status(smoking: int) -> str:
    """Get smoking status"""
    if smoking == 0:
        return "Never Smoked"
    elif smoking == 1:
        return "Former Smoker"
    else:
        return "Current Smoker"

def get_risk_status(risk: float) -> str:
    """Get risk status"""
    if risk < 10:
        return "Low Risk"
    elif risk < 30:
        return "Moderate Risk"
    elif risk < 50:
        return "High Risk"
    else:
        return "Very High Risk"

def get_priority_level(risk: float) -> str:
    """Get priority level"""
    if risk < 10:
        return "Low"
    elif risk < 30:
        return "Medium"
    elif risk < 50:
        return "High"
    else:
        return "Critical"

def get_action_required(score: float) -> str:
    """Get action required based on score"""
    if score >= 85:
        return "Maintain"
    elif score >= 70:
        return "Monitor"
    elif score >= 55:
        return "Improve"
    elif score >= 40:
        return "Focus"
    else:
        return "Urgent"