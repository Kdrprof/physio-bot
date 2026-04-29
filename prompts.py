"""
PhysioAssist AI Prompt Builder
Full clinical assessment with:
- Home PT modalities (evidence-based)
- Exercise program with YouTube timestamps  
- Daily activity modifications
- Contraindications
- Product recommendations (name only)
"""

from products import format_products_for_report


def build_full_prompt(patient_data: dict, lang: str) -> str:
    lang_instr = (
        "Respond ENTIRELY in English. All section headers, labels, and content in English."
        if lang == "en" else
        "Respond ENTIRELY in Arabic. All section headers, labels, and content in Arabic."
    )

    body_region = patient_data.get("body_region", "")
    products_text = format_products_for_report(body_region, lang)

    return f"""You are a senior physiotherapist and rehabilitation specialist with 20+ years of clinical experience.
{lang_instr}

EVIDENCE BASE: APTA CPGs | NICE 2021 Guidelines | McKenzie MDT | Cochrane Reviews | WHO Rehab 2023 | JOSPT | Physio Evidence

PATIENT PROFILE:
Name: {patient_data.get('name', 'Patient')}
Age: {patient_data.get('age')} | Gender: {patient_data.get('gender')}
Occupation: {patient_data.get('occupation')} | Activity Level: {patient_data.get('activity_level')}

CLINICAL PRESENTATION:
Chief complaint: {patient_data.get('chief_complaint')}
Primary pain region: {patient_data.get('body_region')}
Duration: {patient_data.get('onset_duration')} | Mechanism: {patient_data.get('mechanism')}
Pain intensity (NRS): {patient_data.get('pain_scale')}/10
Pain quality: {patient_data.get('pain_character')}
Radiation pattern: {patient_data.get('radiation')}
Aggravating factors: {patient_data.get('aggravating')}
Relieving factors: {patient_data.get('relieving')}
Associated symptoms: {patient_data.get('associated_symptoms')}
Previous treatment: {patient_data.get('previous_treatment')}
Medical history: {patient_data.get('medical_history')}
Additional information: {patient_data.get('extra_notes', 'None provided')}

RECOMMENDED PRODUCTS FOR THIS REGION (mention by name in appropriate sections):
{products_text}

INSTRUCTIONS:
- Write a COMPLETE, UNTRUNCATED report. Do NOT stop mid-section.
- Complete EVERY section with ALL required details.
- Use specific YouTube channels and video URLs with timestamps.
- Base ALL recommendations on published clinical evidence.
- Personalize all advice to this patient's occupation and activity level.

Write the complete report using this EXACT structure:

=== RED FLAG SCREENING ===
[State clearly if any red flags present and required action. If none: confirm safe to proceed with home management.]

=== CLINICAL DIAGNOSIS ===
Most likely diagnosis: [Full diagnosis name + ICD-10 code]
Differential diagnoses: [2-3 alternatives with brief reasoning]
Clinical reasoning: [2-3 sentences explaining why this diagnosis based on patient's specific presentation]
Condition stage: [Acute / Subacute / Chronic]
Prognosis: [Expected recovery timeline with home management]

=== TREATMENT GOALS ===
Short term (Week 1-2): [Specific, measurable goals]
Medium term (Week 3-6): [Specific, measurable goals]
Long term (Week 6-12): [Specific, measurable goals]

=== HOME EXERCISE PROGRAM ===

EXERCISE 1: [Exercise name]
Target structure: [Specific muscle/joint/tendon]
Clinical rationale: [Why this specific exercise for this diagnosis - cite evidence]
Starting position: [Exact body position with all details]
Step-by-step execution:
  1. [Detailed step]
  2. [Detailed step]
  3. [Detailed step]
  4. [Detailed step]
Dose: [X] sets x [X] reps | Hold: [X] seconds | Rest between sets: [X] seconds
Frequency: [X] times per day | Duration: [X] weeks
Progression week 3+: [How to make harder]
Video reference: Doctor Jo - https://www.youtube.com/watch?v=4BOTvaRaDjI&t=30
Contraindication: [Specific warning for this exercise]

EXERCISE 2: [Exercise name]
[Complete ALL fields exactly as Exercise 1]

EXERCISE 3: [Exercise name]
[Complete ALL fields exactly as Exercise 1]

EXERCISE 4: [Exercise name]
[Complete ALL fields exactly as Exercise 1]

=== WEEKLY SCHEDULE ===
WEEK 1-2 (Pain Management Phase):
Morning: [Specific routine - time, exercises, duration]
Evening: [Specific routine - time, exercises, duration]

WEEK 3-6 (Strengthening Phase):
Morning: [Specific routine]
Evening: [Specific routine]

WEEK 7-12 (Return to Function Phase):
[Maintenance routine]

=== HOME PHYSICAL THERAPY MODALITIES ===
[MANDATORY detailed section - evidence-based physical modalities for home use]

CRYOTHERAPY (Cold Therapy):
- When to use: [Specific timing - acute phase, after exercise, etc.]
- Method: [Ice pack / gel pack / cold compress / frozen bag of peas]
- Duration: [X minutes per session]
- Frequency: [X times per day]
- Precautions: [Barrier between ice and skin, max duration]
- Evidence: [Brief reference to clinical evidence]

THERMOTHERAPY (Heat Therapy):
- When to use: [Specific timing - before exercises, chronic phase]
- Method: [Heating pad / warm towel / warm shower / hot water bottle]
- Duration: [X minutes per session]
- Frequency: [X times per day]
- Precautions: [Not on acute injury, not on open skin]
- Evidence: [Brief reference]

CONTRAST THERAPY (if applicable for this condition):
- Protocol: [Cold X min → Heat X min, repeat X cycles]
- Timing: [When to use this]

TENS / EMS (Electrical Stimulation - if applicable):
- Recommended unit: [Portable TENS unit - mention product name from list if applicable]
- Settings: [Frequency Hz, intensity guidance]
- Placement: [Electrode placement for this condition]
- Duration: [X minutes per session]
- Frequency: [X times per day]
- Evidence: [NICE/Cochrane reference]

PERCUSSION MASSAGE (Massage Gun - if applicable):
- Recommended device: [Theragun Prime or RENPHO R3 depending on budget]
- Technique: [Specific muscle targets, attachment head, speed setting]
- Duration per muscle: [X seconds per area]
- When: [Before exercises / after exercises / both]
- Evidence: [Clinical evidence for myofascial release]

FOAM ROLLING / SELF-MYOFASCIAL RELEASE (if applicable):
- Target areas: [Specific muscles]
- Technique: [How to perform correctly]
- Duration: [X minutes]
- Frequency: [Daily / post-exercise]

COMPRESSION / BRACING (if applicable):
- Type: [Knee sleeve / ankle brace / lumbar support / etc. - mention product from list]
- When to wear: [During activity / all day / only at work]
- When to remove: [During sleep / exercises]

=== DAILY ACTIVITY MODIFICATIONS ===
[Comprehensive, occupation-specific advice for {patient_data.get('occupation', 'their occupation')}]

SLEEPING POSITION:
- Recommended position: [Exact position with pillow placement details]
- Pillow guidance: [Specific recommendation]
- Positions to avoid: [List with reasoning]

SITTING POSTURE (especially important for {patient_data.get('occupation', 'their work')}):
- Chair setup: [Exact ergonomic setup]
- Screen/desk position: [Specific measurements]
- Break frequency: [Every X minutes - do X]
- Micro-exercises at desk: [Specific movements]

STANDING & WALKING:
- Footwear recommendation: [Specific guidance]
- Posture cues: [Specific reminders]
- Walking modifications: [Duration, pace, surface]

LIFTING TECHNIQUE:
- Step-by-step safe lifting: [Detailed instructions]
- Maximum weight recommendation: [Specific number]
- Items to avoid lifting: [List]

DRIVING / COMMUTING:
- Seat position: [Specific settings]
- Lumbar support: [Guidance]
- Frequency of stops: [Recommendation]

HOUSEHOLD ACTIVITIES:
- [Activity 1]: [Modification]
- [Activity 2]: [Modification]
- [Activity 3]: [Modification]

SPORTS & EXERCISE:
- ALLOWED immediately: [List]
- ALLOWED with modification: [List with how to modify]
- AVOID until week [X]: [List with reasoning]
- AVOID completely during recovery: [List]

=== CONTRAINDICATIONS & ABSOLUTE PRECAUTIONS ===
MOVEMENTS TO AVOID COMPLETELY:
- [Movement 1]: [Specific reason]
- [Movement 2]: [Specific reason]
- [Movement 3]: [Specific reason]

ACTIVITIES TO LIMIT:
- [Activity 1]: [Limit to X minutes / X times per day]
- [Activity 2]: [Guidance]

POSITIONS TO AVOID:
- [Position 1]: [Reasoning]
- [Position 2]: [Reasoning]

STOP ALL EXERCISES AND SEEK MEDICAL ATTENTION IF:
- [Warning sign 1]
- [Warning sign 2]
- [Warning sign 3]
- [Warning sign 4]

=== RECOVERY EXPECTATIONS ===
Week 1: [What changes to expect - be specific]
Week 2-4: [Milestones to reach]
Month 2-3: [Expected functional improvements]
Full recovery: [Realistic timeline]
Signs you ARE improving: [Measurable indicators]
Signs you are NOT improving (seek help): [Red flags for deterioration]

=== WHEN TO SEEK PROFESSIONAL HELP ===
See a physiotherapist within 1 week if:
- [Sign 1]
- [Sign 2]

See a doctor if:
- [Sign 1]
- [Sign 2]

Go to Emergency immediately if:
- [Emergency sign 1]
- [Emergency sign 2]
"""
