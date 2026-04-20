RELATION_PROMPT = """\
You are a pharmacovigilance expert. Analyze this Hinglish patient narrative and determine the relationship between the identified drug and symptom.

Narrative: {clean_text}
Drug entity: {drug_span}
Symptom entity: {symptom_span}

Classify as exactly one of: Causes-ADR, Treats-Indication, No-Relation

Extract evidence:
- temporal_marker: time-indicating phrase if present (e.g. "ke baad", "lene ke baad") or null
- temporal_marker_translation: English translation of temporal marker or null
- negation_detected: true or false — look for "nahi", "nahin", "no", "not", "nahi hua"
- causal_pattern: one of [temporal_proximity_post_ingestion, patient_self_attribution, concurrent_occurrence, negative_association, no_clear_pattern]
- plain_language_reason: one English sentence explaining the classification

Few-shot examples:

Example 1:
Narrative: "Maine metformin 500mg li aur subah uthke ulti jaisi feeling thi"
Drug: metformin 500mg | Symptom: ulti jaisi feeling
{{"relation_type":"Causes-ADR","confidence":0.91,"temporal_marker":"lene ke baad","temporal_marker_translation":"after taking","negation_detected":false,"causal_pattern":"temporal_proximity_post_ingestion","plain_language_reason":"Patient reports nausea-like sensation after taking metformin, with temporal sequence indicating causal relationship."}}

Example 2:
Narrative: "Amlodipine le raha hun blood pressure ke liye, chakkar aa rahe hain"
Drug: amlodipine | Symptom: chakkar
{{"relation_type":"Causes-ADR","confidence":0.84,"temporal_marker":null,"temporal_marker_translation":null,"negation_detected":false,"causal_pattern":"patient_self_attribution","plain_language_reason":"Patient reports dizziness while taking amlodipine for blood pressure, suggesting an adverse drug reaction."}}

Example 3:
Narrative: "Aspirin le raha hun sar dard ke liye"
Drug: aspirin | Symptom: sar dard
{{"relation_type":"Treats-Indication","confidence":0.88,"temporal_marker":null,"temporal_marker_translation":null,"negation_detected":false,"causal_pattern":"no_clear_pattern","plain_language_reason":"Patient is taking aspirin specifically to treat headache, indicating therapeutic use not an adverse reaction."}}

Example 4:
Narrative: "Metformin lene ke baad chakkar nahi aaya"
Drug: metformin | Symptom: chakkar
{{"relation_type":"No-Relation","confidence":0.92,"temporal_marker":"lene ke baad","temporal_marker_translation":"after taking","negation_detected":true,"causal_pattern":"negative_association","plain_language_reason":"Patient explicitly states no dizziness occurred after taking metformin — negation detected."}}

Example 5:
Narrative: "Atorvastatin khane ke baad pair mein dard ho raha hai, kal se"
Drug: atorvastatin | Symptom: dard
{{"relation_type":"Causes-ADR","confidence":0.87,"temporal_marker":"khane ke baad","temporal_marker_translation":"after eating/taking","negation_detected":false,"causal_pattern":"temporal_proximity_post_ingestion","plain_language_reason":"Patient reports leg pain appearing after starting atorvastatin, consistent with known myalgia side effect."}}

Example 6:
Narrative: "Ibuprofen se pet mein jalan ho rahi hai"
Drug: ibuprofen | Symptom: jalan
{{"relation_type":"Causes-ADR","confidence":0.89,"temporal_marker":"se","temporal_marker_translation":"from/because of","negation_detected":false,"causal_pattern":"patient_self_attribution","plain_language_reason":"Patient directly attributes gastric burning to ibuprofen using causal preposition 'se'."}}

Now classify:
Narrative: {clean_text}
Drug: {drug_span}
Symptom: {symptom_span}

Respond ONLY with the JSON object, no other text:"""
