"""
PhysioAssist Clinical Self-Assessment Tests
Evidence-based provocative tests per body region
Sources: JOSPT, Cochrane, Magee Orthopedic Assessment, Maitland, IFOMPT
"""

# Each test:
# name, instruction, video_id, start_sec, end_sec, responses, clinical_meaning

CLINICAL_TESTS = {

    "Lower Back / Pelvis": [
        {
            "key": "slr",
            "name_en": "Straight Leg Raise (SLR) Test",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0631\u0641\u0639 \u0627\u0644\u0633\u0627\u0642 \u0627\u0644\u0645\u0645\u062f\u0648\u062f\u0629",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: SLR (Nerve Root Test)</b>\n\n"
                "1. Lie flat on your back on a firm surface\n"
                "2. Keep one leg straight, flex the other knee\n"
                "3. Slowly raise the STRAIGHT leg upward\n"
                "4. Keep knee fully extended\n"
                "5. Stop when you feel pain or tightness\n\n"
                "\u26a0\ufe0f Note the angle where pain starts and WHERE you feel it"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0631\u0641\u0639 \u0627\u0644\u0633\u0627\u0642 \u0627\u0644\u0645\u0645\u062f\u0648\u062f\u0629</b>\n\n"
                "1. \u0627\u0633\u062a\u0644\u0642\u0650 \u0639\u0644\u0649 \u0638\u0647\u0631\u0643 \u0639\u0644\u0649 \u0633\u0637\u062d \u0635\u0644\u0628\n"
                "2. \u0627\u0628\u0642\u0650 \u0633\u0627\u0642\u0627\u064b \u0645\u0645\u062f\u0648\u062f\u0629\u060c \u0627\u062b\u0646\u0650 \u0627\u0644\u0623\u062e\u0631\u0649\n"
                "3. \u0627\u0631\u0641\u0639 \u0627\u0644\u0633\u0627\u0642 \u0627\u0644\u0645\u0645\u062f\u0648\u062f\u0629 \u0628\u0628\u0637\u0621\n"
                "4. \u0623\u0628\u0642\u0650 \u0627\u0644\u0631\u0643\u0628\u0629 \u0645\u0645\u062f\u0648\u062f\u0629 \u062a\u0645\u0627\u0645\u0627\u064b\n"
                "5. \u062a\u0648\u0642\u0651\u0641 \u0639\u0646\u062f \u0627\u0644\u0634\u0639\u0648\u0631 \u0628\u0627\u0644\u0623\u0644\u0645\n\n"
                "\u26a0\ufe0f \u0644\u0627\u062d\u0638 \u0623\u064a\u0646 \u062a\u0634\u0639\u0631 \u0628\u0627\u0644\u0623\u0644\u0645"
            ),
            "video_id": "lbozu0DPcYI",
            "start_sec": 30, "end_sec": 90,
            "responses_en": ["Pain shoots down leg below knee", "Pain in buttock only", "Back tightness only", "No pain at all"],
            "responses_ar": ["\u0623\u0644\u0645 \u064a\u0646\u062a\u0634\u0631 \u0644\u0644\u0633\u0627\u0642 \u062a\u062d\u062a \u0627\u0644\u0631\u0643\u0628\u0629", "\u0623\u0644\u0645 \u0641\u064a \u0627\u0644\u0645\u0624\u062e\u0631\u0629 \u0641\u0642\u0637", "\u062a\u0634\u0646\u062c \u0641\u064a \u0627\u0644\u0638\u0647\u0631 \u0641\u0642\u0637", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Pain shoots down leg below knee": {"diagnosis_hint": "Lumbar radiculopathy / disc herniation", "score": 3},
                "Pain in buttock only": {"diagnosis_hint": "Possible SI joint or piriformis", "score": 1},
                "Back tightness only": {"diagnosis_hint": "Hamstring tightness / mechanical LBP", "score": 0},
                "No pain at all": {"diagnosis_hint": "SLR negative — less likely radiculopathy", "score": 0},
            }
        },
        {
            "key": "mckenzie",
            "name_en": "McKenzie Extension Test",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u0628\u0633\u0637 \u0627\u0644\u0645\u062d\u0648\u0631\u064a (McKenzie)",
            "instruction_en": (
                "\U0001f3ac <b>Test 2: McKenzie Extension</b>\n\n"
                "1. Lie face DOWN on a firm surface\n"
                "2. Place hands under your shoulders\n"
                "3. Slowly press up — lift ONLY your upper body\n"
                "4. Hips stay on the floor\n"
                "5. Hold 3 seconds, repeat 5 times\n\n"
                "\u26a0\ufe0f Does your leg pain MOVE toward your back? (centralization = good sign)"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 2: \u0628\u0633\u0637 McKenzie</b>\n\n"
                "1. \u0627\u0633\u062a\u0644\u0642\u0650 \u0639\u0644\u0649 \u0628\u0637\u0646\u0643\n"
                "2. \u0636\u0639 \u064a\u062f\u064a\u0643 \u062a\u062d\u062a \u0643\u062a\u0641\u064a\u0643\n"
                "3. \u0627\u0631\u0641\u0639 \u062c\u0633\u0645\u0643 \u0627\u0644\u0639\u0644\u0648\u064a \u0628\u0628\u0637\u0621\n"
                "4. \u0627\u0628\u0642\u0650 \u0627\u0644\u062d\u0648\u0636 \u0639\u0644\u0649 \u0627\u0644\u0623\u0631\u0636\n"
                "5. \u0627\u062b\u0628\u062a 3 \u062b\u0648\u0627\u0646\u064a\u060c \u0643\u0631\u0651\u0631 5 \u0645\u0631\u0627\u062a\n\n"
                "\u26a0\ufe0f \u0647\u0644 \u0623\u0644\u0645 \u0627\u0644\u0633\u0627\u0642 \u064a\u062a\u062d\u0631\u0643 \u0646\u062d\u0648 \u0627\u0644\u0638\u0647\u0631\u061f"
            ),
            "video_id": "FDwpEdxZ4H4",
            "start_sec": 20, "end_sec": 75,
            "responses_en": ["Leg pain moves toward back (centralization)", "Leg pain increases", "Back pain only — no leg change", "No change at all"],
            "responses_ar": ["\u0623\u0644\u0645 \u0627\u0644\u0633\u0627\u0642 \u062a\u062d\u0631\u0643 \u0646\u062d\u0648 \u0627\u0644\u0638\u0647\u0631", "\u0623\u0644\u0645 \u0627\u0644\u0633\u0627\u0642 \u064a\u0632\u062f\u0627\u062f", "\u0623\u0644\u0645 \u0627\u0644\u0638\u0647\u0631 \u0641\u0642\u0637", "\u0644\u0627 \u062a\u063a\u064a\u064a\u0631"],
            "scoring": {
                "Leg pain moves toward back (centralization)": {"diagnosis_hint": "McKenzie Derangement — disc herniation responds well to extension", "score": 3},
                "Leg pain increases": {"diagnosis_hint": "Peripheralization — avoid extension, consider flexion bias", "score": 2},
                "Back pain only — no leg change": {"diagnosis_hint": "Mechanical LBP without radiculopathy", "score": 1},
                "No change at all": {"diagnosis_hint": "Postural or other non-disc cause", "score": 0},
            }
        },
    ],

    "Neck / Head": [
        {
            "key": "spurling",
            "name_en": "Spurling's Test (Cervical Compression)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0633\u0628\u0648\u0631\u0644\u064a\u0646\u063a",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Spurling's Test</b>\n\n"
                "1. Sit upright in a chair\n"
                "2. Tilt your head to the PAINFUL side\n"
                "3. Rotate slightly toward painful side\n"
                "4. Ask someone to gently press DOWN on your head\n"
                "   (If alone: just tilt and rotate, then look up)\n\n"
                "\u26a0\ufe0f Does pain shoot into your arm or fingers?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0636\u063a\u0637 \u0639\u0645\u0648\u062f \u0627\u0644\u0641\u0642\u0631\u0627\u062a \u0627\u0644\u0639\u0646\u0642\u064a\u0629</b>\n\n"
                "1. \u0627\u062c\u0644\u0633 \u0645\u0633\u062a\u0642\u064a\u0645\u0627\u064b\n"
                "2. \u0623\u0645\u0644 \u0631\u0623\u0633\u0643 \u0646\u062d\u0648 \u062c\u0627\u0646\u0628 \u0627\u0644\u0623\u0644\u0645\n"
                "3. \u062f\u0648\u0651\u0631 \u0642\u0644\u064a\u0644\u0627\u064b \u0646\u062d\u0648 \u0646\u0641\u0633 \u0627\u0644\u062c\u0627\u0646\u0628\n"
                "4. \u0627\u0637\u0644\u0628 \u0645\u0646 \u0634\u062e\u0635 \u0627\u0644\u0636\u063a\u0637 \u0628\u0631\u0641\u0642 \u0639\u0644\u0649 \u0631\u0623\u0633\u0643\n\n"
                "\u26a0\ufe0f \u0647\u0644 \u064a\u0646\u062a\u0634\u0631 \u0627\u0644\u0623\u0644\u0645 \u0644\u0644\u0630\u0631\u0627\u0639 \u0623\u0648 \u0627\u0644\u0623\u0635\u0627\u0628\u0639\u061f"
            ),
            "video_id": "dzLt4Cg5fwY",
            "start_sec": 45, "end_sec": 100,
            "responses_en": ["Pain/tingling shoots into arm or fingers", "Local neck pain only", "Headache reproduced", "No change"],
            "responses_ar": ["\u0623\u0644\u0645 / \u062a\u0646\u0645\u064a\u0644 \u064a\u0646\u062a\u0634\u0631 \u0644\u0644\u0630\u0631\u0627\u0639", "\u0623\u0644\u0645 \u0645\u062d\u0644\u064a \u0641\u0642\u0637", "\u0635\u062f\u0627\u0639 \u0645\u062a\u0643\u0631\u0631", "\u0644\u0627 \u062a\u063a\u064a\u064a\u0631"],
            "scoring": {
                "Pain/tingling shoots into arm or fingers": {"diagnosis_hint": "Cervical radiculopathy — nerve root compression", "score": 3},
                "Local neck pain only": {"diagnosis_hint": "Facet joint or muscular — not radicular", "score": 1},
                "Headache reproduced": {"diagnosis_hint": "Cervicogenic headache", "score": 2},
                "No change": {"diagnosis_hint": "Spurling's negative", "score": 0},
            }
        },
        {
            "key": "cervical_rotation",
            "name_en": "Cervical Rotation Test",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u062f\u0648\u0631\u0627\u0646 \u0627\u0644\u0631\u0642\u0628\u0629",
            "instruction_en": (
                "\U0001f3ac <b>Test 2: Cervical Rotation</b>\n\n"
                "1. Sit upright, eyes forward\n"
                "2. Slowly rotate head LEFT as far as comfortable\n"
                "3. Note any pain, restriction, or dizziness\n"
                "4. Return to center\n"
                "5. Slowly rotate head RIGHT\n"
                "6. Compare both sides\n\n"
                "\u26a0\ufe0f Which direction is MORE restricted or painful?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 2: \u062f\u0648\u0631\u0627\u0646 \u0627\u0644\u0631\u0642\u0628\u0629</b>\n\n"
                "1. \u0627\u062c\u0644\u0633 \u0645\u0633\u062a\u0642\u064a\u0645\u0627\u064b\n"
                "2. \u062f\u0648\u0651\u0631 \u0631\u0623\u0633\u0643 \u064a\u0633\u0627\u0631\u0627\u064b \u0628\u0628\u0637\u0621\n"
                "3. \u0644\u0627\u062d\u0638 \u0623\u064a \u0623\u0644\u0645 \u0623\u0648 \u062f\u0648\u062e\u0629\n"
                "4. \u0639\u062f \u0644\u0644\u0645\u0631\u0643\u0632\u060c \u062b\u0645 \u064a\u0645\u064a\u0646\u0627\u064b\n"
                "5. \u0642\u0627\u0631\u0646 \u0628\u064a\u0646 \u0627\u0644\u062c\u0627\u0646\u0628\u064a\u0646\n\n"
                "\u26a0\ufe0f \u0623\u064a \u0627\u062a\u062c\u0627\u0647 \u0623\u0643\u062b\u0631 \u062a\u0642\u064a\u064a\u062f\u0627\u064b \u0623\u0648 \u0623\u0644\u0645\u0627\u064b\u061f"
            ),
            "video_id": "J4SSoLpQfpA",
            "start_sec": 15, "end_sec": 60,
            "responses_en": ["Painful side only restricted", "Both sides restricted equally", "Dizziness with rotation", "Normal range both sides"],
            "responses_ar": ["\u062a\u0642\u064a\u064a\u062f \u062c\u0627\u0646\u0628 \u0627\u0644\u0623\u0644\u0645 \u0641\u0642\u0637", "\u0643\u0644\u0627 \u0627\u0644\u062c\u0627\u0646\u0628\u064a\u0646 \u0645\u062a\u0642\u064a\u062f\u0627\u0646", "\u062f\u0648\u062e\u0629 \u0645\u0639 \u0627\u0644\u062f\u0648\u0631\u0627\u0646", "\u062d\u0631\u0643\u0629 \u0637\u0628\u064a\u0639\u064a\u0629"],
            "scoring": {
                "Painful side only restricted": {"diagnosis_hint": "Unilateral facet restriction or muscle spasm", "score": 2},
                "Both sides restricted equally": {"diagnosis_hint": "Bilateral restriction — OA or chronic stiffness", "score": 1},
                "Dizziness with rotation": {"diagnosis_hint": "Possible VBI — refer to physician before treatment", "score": 3},
                "Normal range both sides": {"diagnosis_hint": "Good mobility — less likely structural issue", "score": 0},
            }
        },
    ],

    "Shoulder": [
        {
            "key": "hawkins",
            "name_en": "Hawkins-Kennedy Test (Impingement)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0647\u0648\u0643\u064a\u0646\u0632-\u0643\u064a\u0646\u064a\u062f\u064a",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Hawkins-Kennedy (Impingement)</b>\n\n"
                "1. Raise your arm forward to 90 degrees (like pointing ahead)\n"
                "2. Bend elbow to 90 degrees\n"
                "3. With your other hand, ROTATE forearm DOWNWARD\n"
                "   (internal rotation)\n"
                "4. Do slowly and stop if painful\n\n"
                "\u26a0\ufe0f Does this reproduce your shoulder pain?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0627\u0644\u062a\u0636\u064a\u0642 \u0641\u064a \u0627\u0644\u0643\u062a\u0641</b>\n\n"
                "1. \u0627\u0631\u0641\u0639 \u0630\u0631\u0627\u0639\u0643 \u0644\u0644\u0623\u0645\u0627\u0645 90 \u062f\u0631\u062c\u0629\n"
                "2. \u0627\u062b\u0646\u0650 \u0627\u0644\u0643\u0648\u0639 90 \u062f\u0631\u062c\u0629\n"
                "3. \u0628\u0627\u0644\u064a\u062f \u0627\u0644\u0623\u062e\u0631\u0649\u060c \u062f\u0648\u0651\u0631 \u0627\u0644\u0633\u0627\u0639\u062f \u0644\u0644\u0623\u0633\u0641\u0644\n"
                "4. \u0628\u0628\u0637\u0621\u060c \u062a\u0648\u0642\u0651\u0641 \u0639\u0646\u062f \u0627\u0644\u0623\u0644\u0645\n\n"
                "\u26a0\ufe0f \u0647\u0644 \u062a\u0639\u064a\u062f \u0625\u0646\u062a\u0627\u062c \u0623\u0644\u0645 \u0643\u062a\u0641\u0643\u061f"
            ),
            "video_id": "VV2T67pAmI4",
            "start_sec": 20, "end_sec": 70,
            "responses_en": ["Exact shoulder pain reproduced", "Different pain location", "Clicking/catching sensation", "No pain at all"],
            "responses_ar": ["\u0646\u0641\u0633 \u0623\u0644\u0645 \u0627\u0644\u0643\u062a\u0641 \u062a\u0643\u0631\u0651\u0631", "\u0623\u0644\u0645 \u0641\u064a \u0645\u0643\u0627\u0646 \u0645\u062e\u062a\u0644\u0641", "\u0635\u0648\u062a \u0641\u0631\u0642\u0639\u0629 \u0623\u0648 \u0627\u0644\u062a\u0642\u0627\u0637", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Exact shoulder pain reproduced": {"diagnosis_hint": "Positive Hawkins — subacromial impingement or RCT", "score": 3},
                "Different pain location": {"diagnosis_hint": "AC joint or other structure — less likely impingement", "score": 1},
                "Clicking/catching sensation": {"diagnosis_hint": "Possible labral involvement", "score": 2},
                "No pain at all": {"diagnosis_hint": "Hawkins negative — less likely impingement", "score": 0},
            }
        },
        {
            "key": "empty_can",
            "name_en": "Empty Can Test (Supraspinatus)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u0639\u0644\u0628\u0629 \u0627\u0644\u0641\u0627\u0631\u063a\u0629",
            "instruction_en": (
                "\U0001f3ac <b>Test 2: Empty Can Test</b>\n\n"
                "1. Raise both arms to the side at 90 degrees\n"
                "2. Move arms 30 degrees FORWARD (like a Y shape)\n"
                "3. Rotate thumbs DOWN (as if emptying a can)\n"
                "4. Try to hold this position against gravity\n"
                "5. Notice: pain? weakness? arm drops?\n\n"
                "\u26a0\ufe0f Compare both arms — is one weaker?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 2: \u0642\u0648\u0629 \u0627\u0644\u0643\u0641\u0629 \u0627\u0644\u0641\u0648\u0642\u064a\u0629</b>\n\n"
                "1. \u0627\u0631\u0641\u0639 \u0643\u0644\u0627 \u0627\u0644\u0630\u0631\u0627\u0639\u064a\u0646 \u062c\u0627\u0646\u0628\u064a\u0627\u064b 90 \u062f\u0631\u062c\u0629\n"
                "2. \u062d\u0631\u0651\u0643\u0647\u0645\u0627 30 \u062f\u0631\u062c\u0629 \u0644\u0644\u0623\u0645\u0627\u0645\n"
                "3. \u0623\u062f\u0631 \u0627\u0644\u0625\u0628\u0647\u0627\u0645 \u0644\u0644\u0623\u0633\u0641\u0644\n"
                "4. \u062d\u0627\u0648\u0644 \u062a\u062b\u0628\u064a\u062a \u0647\u0630\u0627 \u0627\u0644\u0648\u0636\u0639\n\n"
                "\u26a0\ufe0f \u0647\u0644 \u0630\u0631\u0627\u0639 \u0623\u0636\u0639\u0641 \u0645\u0646 \u0627\u0644\u0623\u062e\u0631\u0649\u061f"
            ),
            "video_id": "K5hzSbzFbWI",
            "start_sec": 10, "end_sec": 55,
            "responses_en": ["Pain AND weakness on affected side", "Pain only, no weakness", "Weakness without pain", "Normal strength both sides"],
            "responses_ar": ["\u0623\u0644\u0645 \u0648\u0636\u0639\u0641 \u0645\u0639\u0627\u064b", "\u0623\u0644\u0645 \u0641\u0642\u0637", "\u0636\u0639\u0641 \u0628\u062f\u0648\u0646 \u0623\u0644\u0645", "\u0642\u0648\u0629 \u0637\u0628\u064a\u0639\u064a\u0629"],
            "scoring": {
                "Pain AND weakness on affected side": {"diagnosis_hint": "Rotator cuff tear (partial or full) — significant finding", "score": 3},
                "Pain only, no weakness": {"diagnosis_hint": "Tendinopathy without tear", "score": 2},
                "Weakness without pain": {"diagnosis_hint": "Possible neurological involvement", "score": 2},
                "Normal strength both sides": {"diagnosis_hint": "Empty can negative", "score": 0},
            }
        },
    ],

    "Knee": [
        {
            "key": "clarkes",
            "name_en": "Clarke's Sign (Patellofemoral Test)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0643\u0644\u0627\u0631\u0643 (\u0627\u0644\u0631\u0636\u0641\u0629 \u0627\u0644\u0635\u063a\u064a\u0631\u0629)",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Clarke's Sign</b>\n\n"
                "1. Sit with leg STRAIGHT on a flat surface\n"
                "2. Place your hand just ABOVE your kneecap\n"
                "3. Apply gentle downward pressure on the kneecap\n"
                "4. Try to tighten your thigh muscle (quad)\n"
                "5. Notice: pain under or around kneecap?\n\n"
                "\u26a0\ufe0f Pain behind the kneecap = positive test"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u0631\u0636\u0641\u0629</b>\n\n"
                "1. \u0627\u062c\u0644\u0633 \u0648\u0627\u0644\u0633\u0627\u0642 \u0645\u0645\u062f\u0648\u062f\u0629\n"
                "2. \u0636\u0639 \u064a\u062f\u0643 \u0641\u0648\u0642 \u0627\u0644\u0631\u0636\u0641\u0629 \u0645\u0628\u0627\u0634\u0631\u0629\n"
                "3. \u0627\u0636\u063a\u0637 \u0628\u0631\u0641\u0642 \u0644\u0644\u0623\u0633\u0641\u0644\n"
                "4. \u062d\u0627\u0648\u0644 \u0634\u062f \u0639\u0636\u0644\u0629 \u0627\u0644\u0641\u062e\u0630\n\n"
                "\u26a0\ufe0f \u0623\u0644\u0645 \u062e\u0644\u0641 \u0627\u0644\u0631\u0636\u0641\u0629 = \u0625\u064a\u062c\u0627\u0628\u064a"
            ),
            "video_id": "F-PUlZqxiRQ",
            "start_sec": 25, "end_sec": 70,
            "responses_en": ["Pain behind/under kneecap", "Pain on inner knee side", "Pain on outer knee side", "No pain"],
            "responses_ar": ["\u0623\u0644\u0645 \u062e\u0644\u0641/\u062a\u062d\u062a \u0627\u0644\u0631\u0636\u0641\u0629", "\u0623\u0644\u0645 \u0627\u0644\u062c\u0627\u0646\u0628 \u0627\u0644\u062f\u0627\u062e\u0644\u064a", "\u0623\u0644\u0645 \u0627\u0644\u062c\u0627\u0646\u0628 \u0627\u0644\u062e\u0627\u0631\u062c\u064a", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Pain behind/under kneecap": {"diagnosis_hint": "Patellofemoral Pain Syndrome (PFPS)", "score": 3},
                "Pain on inner knee side": {"diagnosis_hint": "Medial meniscus or MCL involvement", "score": 2},
                "Pain on outer knee side": {"diagnosis_hint": "IT band syndrome or LCL involvement", "score": 2},
                "No pain": {"diagnosis_hint": "Clarke's negative — less likely PFPS", "score": 0},
            }
        },
        {
            "key": "thessaly",
            "name_en": "Thessaly Test (Meniscus)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u062b\u064a\u0633\u0627\u0644\u064a\u0627 (\u0627\u0644\u063a\u0636\u0631\u0648\u0641 \u0627\u0644\u0647\u0644\u0627\u0644\u064a)",
            "instruction_en": (
                "\U0001f3ac <b>Test 2: Thessaly Test</b>\n\n"
                "1. Stand on the AFFECTED leg only\n"
                "2. Bend knee slightly to 20 degrees\n"
                "3. Hold onto something for balance\n"
                "4. Rotate your body LEFT then RIGHT\n"
                "   while keeping the foot planted\n"
                "5. Do 3 rotations each direction\n\n"
                "\u26a0\ufe0f Pain or clicking at the joint line?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 2: \u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u063a\u0636\u0631\u0648\u0641 \u0627\u0644\u0647\u0644\u0627\u0644\u064a</b>\n\n"
                "1. \u0642\u0641 \u0639\u0644\u0649 \u0633\u0627\u0642 \u0627\u0644\u0623\u0644\u0645 \u0641\u0642\u0637\n"
                "2. \u0627\u062b\u0646\u0650 \u0627\u0644\u0631\u0643\u0628\u0629 20 \u062f\u0631\u062c\u0629\n"
                "3. \u062a\u0645\u0633\u0651\u0643 \u0628\u0634\u064a\u0621 \u0644\u0644\u062a\u0648\u0627\u0632\u0646\n"
                "4. \u062f\u0648\u0651\u0631 \u062c\u0633\u0645\u0643 3 \u0645\u0631\u0627\u062a \u0644\u0643\u0644 \u0627\u062a\u062c\u0627\u0647\n\n"
                "\u26a0\ufe0f \u0623\u0644\u0645 \u0623\u0648 \u0635\u0648\u062a \u0641\u0631\u0642\u0639\u0629 \u0641\u064a \u0627\u0644\u0645\u0641\u0635\u0644\u061f"
            ),
            "video_id": "zQQLjOH9Ptg",
            "start_sec": 15, "end_sec": 60,
            "responses_en": ["Pain or click at joint line (inner/outer)", "General knee discomfort", "Instability feeling", "No pain"],
            "responses_ar": ["\u0623\u0644\u0645 \u0623\u0648 \u0641\u0631\u0642\u0639\u0629 \u0641\u064a \u062e\u0637 \u0627\u0644\u0645\u0641\u0635\u0644", "\u0625\u0632\u0639\u0627\u062c \u0639\u0627\u0645", "\u0634\u0639\u0648\u0631 \u0628\u0639\u062f\u0645 \u0627\u0644\u0627\u0633\u062a\u0642\u0631\u0627\u0631", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Pain or click at joint line (inner/outer)": {"diagnosis_hint": "Meniscal pathology likely", "score": 3},
                "General knee discomfort": {"diagnosis_hint": "Non-specific — could be OA or synovitis", "score": 1},
                "Instability feeling": {"diagnosis_hint": "Possible ligament laxity", "score": 2},
                "No pain": {"diagnosis_hint": "Thessaly negative", "score": 0},
            }
        },
    ],

    "Ankle / Foot": [
        {
            "key": "windlass",
            "name_en": "Windlass Test (Plantar Fascia)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u0644\u0641\u0627\u0641\u0629 (\u0627\u0644\u0644\u0641\u0627\u0641\u0629 \u0627\u0644\u062e\u0637\u064a\u0629)",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Windlass Test</b>\n\n"
                "1. Stand barefoot\n"
                "2. Place toes on a step edge (or doorstep)\n"
                "3. Slowly bend toes UPWARD (toward shin)\n"
                "4. Hold 5 seconds\n"
                "5. Bear weight through the heel\n\n"
                "\u26a0\ufe0f Pain at heel or along arch = positive"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u0644\u0641\u0627\u0641\u0629 \u0627\u0644\u062e\u0637\u064a\u0629</b>\n\n"
                "1. \u0642\u0641 \u062d\u0627\u0641\u064a\u0627\u064b\n"
                "2. \u0636\u0639 \u0623\u0635\u0627\u0628\u0639 \u0627\u0644\u0642\u062f\u0645 \u0639\u0644\u0649 \u062d\u0627\u0641\u0629\n"
                "3. \u0627\u062b\u0646\u0650 \u0627\u0644\u0623\u0635\u0627\u0628\u0639 \u0644\u0644\u0623\u0639\u0644\u0649\n"
                "4. \u0627\u062b\u0628\u062a 5 \u062b\u0648\u0627\u0646\u064a\n\n"
                "\u26a0\ufe0f \u0623\u0644\u0645 \u0641\u064a \u0627\u0644\u0643\u0639\u0628 \u0623\u0648 \u0642\u0648\u0633 \u0627\u0644\u0642\u062f\u0645 = \u0625\u064a\u062c\u0627\u0628\u064a"
            ),
            "video_id": "Kox5GfhOE3w",
            "start_sec": 20, "end_sec": 65,
            "responses_en": ["Sharp pain at heel", "Pain along arch of foot", "Achilles tightness only", "No pain"],
            "responses_ar": ["\u0623\u0644\u0645 \u062d\u0627\u062f \u0641\u064a \u0627\u0644\u0643\u0639\u0628", "\u0623\u0644\u0645 \u0639\u0644\u0649 \u0637\u0648\u0644 \u0642\u0648\u0633 \u0627\u0644\u0642\u062f\u0645", "\u0634\u062f \u0641\u0642\u0637 \u0641\u064a \u0627\u0644\u0648\u062a\u0631 \u0627\u0644\u0623\u062e\u064a\u0644\u0633\u064a", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Sharp pain at heel": {"diagnosis_hint": "Plantar fasciitis — heel spur involvement likely", "score": 3},
                "Pain along arch of foot": {"diagnosis_hint": "Plantar fasciitis — medial band", "score": 3},
                "Achilles tightness only": {"diagnosis_hint": "Achilles involvement — test further", "score": 1},
                "No pain": {"diagnosis_hint": "Windlass negative", "score": 0},
            }
        },
    ],

    "Elbow / Forearm": [
        {
            "key": "mills",
            "name_en": "Mill's Test (Lateral Epicondyle)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0645\u064a\u0644\u0632 (\u0627\u0644\u0644\u0642\u064a\u0637\u0629 \u0627\u0644\u062c\u0627\u0646\u0628\u064a\u0629)",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Mill's Test (Tennis Elbow)</b>\n\n"
                "1. Extend your arm STRAIGHT in front\n"
                "2. Make a FIST with your hand\n"
                "3. Bend your wrist DOWNWARD\n"
                "4. Now try to RESIST as someone pushes wrist down\n"
                "   (Or use other hand to apply resistance)\n\n"
                "\u26a0\ufe0f Pain at the OUTER elbow?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0623\u0644\u0645 \u0627\u0644\u0643\u0648\u0639 \u0627\u0644\u062c\u0627\u0646\u0628\u064a</b>\n\n"
                "1. \u0645\u062f\u0651 \u0630\u0631\u0627\u0639\u0643 \u0644\u0644\u0623\u0645\u0627\u0645\n"
                "2. \u0627\u0642\u0628\u0636 \u0628\u064a\u062f\u0643\n"
                "3. \u0627\u062b\u0646\u0650 \u0627\u0644\u0631\u0633\u063a \u0644\u0644\u0623\u0633\u0641\u0644\n"
                "4. \u0642\u0627\u0648\u0645 \u0648\u0632\u0646 \u0645\u0642\u0627\u0628\u0644 \u0628\u0627\u0644\u064a\u062f \u0627\u0644\u0623\u062e\u0631\u0649\n\n"
                "\u26a0\ufe0f \u0623\u0644\u0645 \u0641\u064a \u0627\u0644\u062c\u0627\u0646\u0628 \u0627\u0644\u062e\u0627\u0631\u062c\u064a \u0644\u0644\u0643\u0648\u0639\u061f"
            ),
            "video_id": "kp_-6kHZ_2w",
            "start_sec": 15, "end_sec": 60,
            "responses_en": ["Pain at outer elbow (lateral)", "Pain at inner elbow (medial)", "Forearm pain only", "No pain"],
            "responses_ar": ["\u0623\u0644\u0645 \u0628\u0627\u0644\u062c\u0627\u0646\u0628 \u0627\u0644\u062e\u0627\u0631\u062c\u064a", "\u0623\u0644\u0645 \u0628\u0627\u0644\u062c\u0627\u0646\u0628 \u0627\u0644\u062f\u0627\u062e\u0644\u064a", "\u0623\u0644\u0645 \u0641\u064a \u0627\u0644\u0633\u0627\u0639\u062f \u0641\u0642\u0637", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Pain at outer elbow (lateral)": {"diagnosis_hint": "Lateral epicondylalgia (Tennis Elbow)", "score": 3},
                "Pain at inner elbow (medial)": {"diagnosis_hint": "Medial epicondylalgia (Golfer's Elbow)", "score": 3},
                "Forearm pain only": {"diagnosis_hint": "Muscle strain or referred pain", "score": 1},
                "No pain": {"diagnosis_hint": "Mill's negative", "score": 0},
            }
        },
    ],

    "Wrist / Hand": [
        {
            "key": "phalens",
            "name_en": "Phalen's Test (Carpal Tunnel)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u0641\u064a\u0644\u0627\u0646\u0632 (\u0627\u0644\u0646\u0641\u0642 \u0627\u0644\u0631\u0633\u063a\u064a)",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Phalen's Test</b>\n\n"
                "1. Hold both wrists bent FULLY downward\n"
                "2. Press the backs of your hands together\n"
                "3. Hold this position for 60 seconds\n"
                "4. Keep elbows relaxed\n\n"
                "\u26a0\ufe0f Tingling/numbness in thumb, index, middle finger = positive"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0627\u062e\u062a\u0628\u0627\u0631 \u0627\u0644\u0646\u0641\u0642 \u0627\u0644\u0631\u0633\u063a\u064a</b>\n\n"
                "1. \u0627\u062b\u0646\u0650 \u0643\u0644\u0627 \u0627\u0644\u0631\u0633\u063a\u064a\u0646 \u0644\u0644\u0623\u0633\u0641\u0644 \u062a\u0645\u0627\u0645\u0627\u064b\n"
                "2. \u0627\u0636\u063a\u0637 \u0638\u0647\u0631 \u0627\u0644\u064a\u062f\u064a\u0646 \u0645\u0639\u0627\u064b\n"
                "3. \u0627\u062d\u062a\u0641\u0638 60 \u062b\u0627\u0646\u064a\u0629\n\n"
                "\u26a0\ufe0f \u062a\u0646\u0645\u064a\u0644 \u0641\u064a \u0627\u0644\u0625\u0628\u0647\u0627\u0645 \u0648\u0627\u0644\u0633\u0628\u0627\u0628\u0629 = \u0625\u064a\u062c\u0627\u0628\u064a"
            ),
            "video_id": "Ud7aDRoiLi8",
            "start_sec": 20, "end_sec": 70,
            "responses_en": ["Tingling in thumb/index/middle finger", "Tingling in ring/little finger", "Wrist pain only", "No symptoms"],
            "responses_ar": ["\u062a\u0646\u0645\u064a\u0644 \u0641\u064a \u0627\u0644\u0625\u0628\u0647\u0627\u0645 \u0648\u0627\u0644\u0633\u0628\u0627\u0628\u0629", "\u062a\u0646\u0645\u064a\u0644 \u0641\u064a \u0627\u0644\u062e\u0646\u0635\u0631 \u0648\u0627\u0644\u0635\u063a\u064a\u0631", "\u0623\u0644\u0645 \u0627\u0644\u0631\u0633\u063a \u0641\u0642\u0637", "\u0644\u0627 \u0623\u0639\u0631\u0627\u0636"],
            "scoring": {
                "Tingling in thumb/index/middle finger": {"diagnosis_hint": "Carpal Tunnel Syndrome — median nerve distribution", "score": 3},
                "Tingling in ring/little finger": {"diagnosis_hint": "Ulnar nerve — cubital tunnel rather than CTS", "score": 2},
                "Wrist pain only": {"diagnosis_hint": "Mechanical wrist issue — not CTS", "score": 1},
                "No symptoms": {"diagnosis_hint": "Phalen's negative", "score": 0},
            }
        },
    ],

    "Hip / Thigh": [
        {
            "key": "faber",
            "name_en": "FABER Test (Hip / SI Joint)",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 FABER (\u0627\u0644\u0648\u0631\u0643 / \u0627\u0644\u0645\u0641\u0635\u0644 \u0627\u0644\u0639\u062c\u0632\u064a)",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: FABER Test</b>\n\n"
                "1. Lie on your back\n"
                "2. Place the AFFECTED leg's ankle on the opposite knee\n"
                "   (figure-4 position)\n"
                "3. Let the knee drop toward the floor\n"
                "4. Gently press down on the bent knee\n\n"
                "\u26a0\ufe0f Where do you feel pain or restriction?"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u0627\u062e\u062a\u0628\u0627\u0631 FABER</b>\n\n"
                "1. \u0627\u0633\u062a\u0644\u0642\u0650 \u0639\u0644\u0649 \u0638\u0647\u0631\u0643\n"
                "2. \u0636\u0639 \u0643\u0627\u062d\u0644 \u0627\u0644\u0633\u0627\u0642 \u0627\u0644\u0645\u0624\u0644\u0645\u0629 \u0639\u0644\u0649 \u0631\u0643\u0628\u0629 \u0627\u0644\u0623\u062e\u0631\u0649\n"
                "3. \u062f\u0639 \u0627\u0644\u0631\u0643\u0628\u0629 \u062a\u0633\u0642\u0637 \u0644\u0644\u062c\u0627\u0646\u0628\n"
                "4. \u0627\u0636\u063a\u0637 \u0628\u0631\u0641\u0642 \u0639\u0644\u0649 \u0627\u0644\u0631\u0643\u0628\u0629\n\n"
                "\u26a0\ufe0f \u0623\u064a\u0646 \u062a\u0634\u0639\u0631 \u0628\u0627\u0644\u0623\u0644\u0645\u061f"
            ),
            "video_id": "52Vt3lRd_4E",
            "start_sec": 20, "end_sec": 65,
            "responses_en": ["Groin pain (inside hip)", "Back/SI joint pain", "Outer hip pain", "No pain — full range"],
            "responses_ar": ["\u0623\u0644\u0645 \u0627\u0644\u0645\u063a\u0628\u0646 (\u062f\u0627\u062e\u0644 \u0627\u0644\u0648\u0631\u0643)", "\u0623\u0644\u0645 \u0627\u0644\u0638\u0647\u0631/\u0639\u062c\u0632\u064a", "\u0623\u0644\u0645 \u062c\u0627\u0646\u0628 \u0627\u0644\u0648\u0631\u0643", "\u0644\u0627 \u0623\u0644\u0645"],
            "scoring": {
                "Groin pain (inside hip)": {"diagnosis_hint": "Hip joint pathology — OA or labral tear", "score": 3},
                "Back/SI joint pain": {"diagnosis_hint": "Sacroiliac joint dysfunction", "score": 3},
                "Outer hip pain": {"diagnosis_hint": "Trochanteric bursitis or IT band", "score": 2},
                "No pain — full range": {"diagnosis_hint": "FABER negative — hip joint less likely", "score": 0},
            }
        },
    ],

    "Upper Back": [
        {
            "key": "thoracic_rotation",
            "name_en": "Thoracic Rotation Test",
            "name_ar": "\u0627\u062e\u062a\u0628\u0627\u0631 \u062f\u0648\u0631\u0627\u0646 \u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631",
            "instruction_en": (
                "\U0001f3ac <b>Test 1: Thoracic Rotation</b>\n\n"
                "1. Sit upright in a chair, arms crossed on chest\n"
                "2. Slowly rotate your upper body LEFT\n"
                "3. Note range and any pain\n"
                "4. Return to center\n"
                "5. Rotate RIGHT and compare\n\n"
                "\u26a0\ufe0f Normal is 35-45 degrees each side"
            ),
            "instruction_ar": (
                "\U0001f3ac <b>\u0627\u0644\u0627\u062e\u062a\u0628\u0627\u0631 1: \u062f\u0648\u0631\u0627\u0646 \u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631</b>\n\n"
                "1. \u0627\u062c\u0644\u0633 \u0645\u0633\u062a\u0642\u064a\u0645\u0627\u064b\u060c \u0630\u0631\u0627\u0639\u0627\u0643 \u0639\u0644\u0649 \u0635\u062f\u0631\u0643\n"
                "2. \u062f\u0648\u0651\u0631 \u062c\u0632\u0621\u0643 \u0627\u0644\u0639\u0644\u0648\u064a \u064a\u0633\u0627\u0631\u0627\u064b\n"
                "3. \u0644\u0627\u062d\u0638 \u0627\u0644\u0623\u0644\u0645 \u0648\u0627\u0644\u0645\u062f\u0649\n"
                "4. \u0642\u0627\u0631\u0646 \u0645\u0639 \u0627\u0644\u064a\u0645\u064a\u0646\n\n"
                "\u26a0\ufe0f \u0627\u0644\u0637\u0628\u064a\u0639\u064a 35-45 \u062f\u0631\u062c\u0629 \u0644\u0643\u0644 \u062c\u0627\u0646\u0628"
            ),
            "video_id": "CnM0iFsGLHo",
            "start_sec": 10, "end_sec": 55,
            "responses_en": ["Painful restriction one side only", "Both sides equally restricted", "Clicking/crepitus with rotation", "Normal range both sides"],
            "responses_ar": ["\u062a\u0642\u064a\u064a\u062f \u0645\u0624\u0644\u0645 \u062c\u0627\u0646\u0628 \u0648\u0627\u062d\u062f", "\u0643\u0644\u0627 \u0627\u0644\u062c\u0627\u0646\u0628\u064a\u0646 \u0645\u062a\u0642\u064a\u062f\u0627\u0646", "\u0641\u0631\u0642\u0639\u0629 \u0645\u0639 \u0627\u0644\u062f\u0648\u0631\u0627\u0646", "\u062d\u0631\u0643\u0629 \u0637\u0628\u064a\u0639\u064a\u0629"],
            "scoring": {
                "Painful restriction one side only": {"diagnosis_hint": "Unilateral facet restriction or rib dysfunction", "score": 2},
                "Both sides equally restricted equally": {"diagnosis_hint": "Bilateral restriction — postural kyphosis or OA", "score": 1},
                "Clicking/crepitus with rotation": {"diagnosis_hint": "Facet joint or costovertebral joint involvement", "score": 2},
                "Normal range both sides": {"diagnosis_hint": "Good mobility — postural or muscular cause more likely", "score": 0},
            }
        },
    ],

    # Fallback for other regions
    "Multiple areas": [],
}

# Arabic region key mapping
REGION_MAP_AR = {
    "\u0627\u0644\u0631\u0642\u0628\u0629 \u0648\u0627\u0644\u0631\u0623\u0633": "Neck / Head",
    "\u0627\u0644\u0643\u062a\u0641": "Shoulder",
    "\u0627\u0644\u0643\u0648\u0639 \u0648\u0627\u0644\u0633\u0627\u0639\u062f": "Elbow / Forearm",
    "\u0627\u0644\u0631\u0633\u063a \u0648\u0627\u0644\u064a\u062f": "Wrist / Hand",
    "\u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631": "Upper Back",
    "\u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631": "Lower Back / Pelvis",
    "\u0627\u0644\u0648\u0631\u0643 \u0648\u0627\u0644\u0641\u062e\u0630": "Hip / Thigh",
    "\u0627\u0644\u0631\u0643\u0628\u0629": "Knee",
    "\u0627\u0644\u0643\u0627\u062d\u0644 \u0648\u0627\u0644\u0642\u062f\u0645": "Ankle / Foot",
    "\u0623\u0643\u062b\u0631 \u0645\u0646 \u0645\u0646\u0637\u0642\u0629": "Multiple areas",
}


def get_tests_for_region(body_region: str) -> list:
    """Return clinical tests for given body region."""
    # Normalize Arabic region names
    region = REGION_MAP_AR.get(body_region, body_region)
    return CLINICAL_TESTS.get(region, [])


def format_assessment_results(results: dict, lang: str) -> str:
    """Format self-assessment results for inclusion in AI prompt."""
    if not results:
        return "No self-assessment tests performed."

    lines = ["=== SELF-ASSESSMENT TEST RESULTS ==="]
    for key, data in results.items():
        lines.append(f"Test: {data.get('test_name', key)}")
        lines.append(f"Patient response: {data.get('response', 'N/A')}")
        lines.append(f"Clinical significance: {data.get('clinical_meaning', 'N/A')}")
        lines.append(f"Diagnostic score: {data.get('score', 0)}/3")
        lines.append("")

    total = sum(d.get('score', 0) for d in results.values())
    lines.append(f"Total provocation score: {total}")
    lines.append("Use these results to refine differential diagnosis accuracy.")
    return "\n".join(lines)


def get_video_url(video_id: str, start_sec: int, end_sec: int) -> str:
    """Generate YouTube embed URL with timestamps."""
    return f"https://www.youtube.com/embed/{video_id}?start={start_sec}&end={end_sec}&rel=0&modestbranding=1"


def get_watch_url(video_id: str, start_sec: int) -> str:
    """Generate YouTube watch URL with start time."""
    return f"https://www.youtube.com/watch?v={video_id}&t={start_sec}s"
