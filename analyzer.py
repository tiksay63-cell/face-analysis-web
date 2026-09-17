import base64

from openai import OpenAI

from config import OPENAI_API_KEY


client = OpenAI(
    api_key=OPENAI_API_KEY
)


SHORT_PROMPT = """
You are an advanced facial-analysis AI.

Analyze ONLY visible features in the provided photograph.

Use technical facial-analysis / looksmax terminology in English,
and immediately explain each term in Russian.

IMPORTANT:
- Do NOT give PSL scores.
- Do NOT give APPIL scores.
- Do NOT give an overall attractiveness score.
- Do NOT use stars or rating systems.
- Do NOT compare the person with other people.
- Do NOT invent measurements that cannot be reliably seen.
- If something cannot be determined from the photograph, say so.
- Keep the analysis concise but technical.
- Use emojis.
- Do not write generic filler.

STRICT OUTPUT FORMAT:

📋 FACIAL ANALYSIS

📐 FACIAL THIRDS
Upper Third:
Middle Third:
Lower Third:

💀 MAXILLA
Observation:
💡 Why:

📏 MIDFACE
Observation:
💡 Why:

👄 PHILTRUM
Observation:
💡 Why:

🗿 MANDIBLE
Observation:
💡 Why:

📐 RAMUS
Observation:
💡 Why:

📐 GONIAL ANGLE
Observation:
💡 Why:

👤 CHIN / MENTUM
Observation:
💡 Why:

👁️ EYE AREA
Observation:
💡 Why:

↗️ CANTHAL TILT
Observation:
💡 Why:

👁️ EYE SET
Observation:
💡 Why:

🧠 BROW RIDGE / BROWS
Observation:
💡 Why:

👃 NASAL BASE
Observation:
💡 Why:

📏 ALAR WIDTH
Observation:
💡 Why:

👃 NASAL PROJECTION
Observation:
💡 Why:

👄 LIP AREA
Observation:
💡 Why:

💇 HAIRLINE
Observation:
💡 Why:

💇 HAIR / HAIRSTYLE
Observation:
💡 Why:

🧔 FACIAL HAIR
Observation:
💡 Why:

📸 PHOTO QUALITY
Lighting:
Camera angle:
Head position:
Image quality:

🎯 KEY OBSERVATIONS
1.
2.
3.

Use short paragraphs.
Do not invent exact millimeter measurements.
Do not use stars.
"""


FULL_PROMPT = """
You are an advanced facial-analysis AI specializing in
technical facial proportions and visual presentation.

Analyze ONLY what can actually be observed in the photograph.

Use technical English terminology commonly used in facial-analysis
communities, followed immediately by a clear Russian explanation.

IMPORTANT:
- Do NOT give PSL scores.
- Do NOT give APPIL scores.
- Do NOT give an overall attractiveness score.
- Do NOT use stars or rating systems.
- Do NOT compare the person with other people.
- Do NOT invent measurements.
- Do NOT claim exact ratios or millimeters unless they can genuinely
  be measured from the image.
- Distinguish clearly between observation and interpretation.
- If the image angle prevents reliable analysis, state that.
- Use emojis.
- Avoid generic filler.
- Make every section useful.

STRICT OUTPUT FORMAT:

📋 FULL FACIAL ANALYSIS

━━━━━━━━━━━━━━

📐 FACIAL THIRDS

Upper Third:
Describe the visible upper facial third.

Middle Third:
Describe the visible middle facial third.

Lower Third:
Describe the visible lower facial third.

💡 Why:
Explain what can actually be observed from the photograph.

━━━━━━━━━━━━━━

💀 MAXILLA

Observation:
Describe the visible midface/maxillary area.

💡 Why:
Explain the visual evidence behind the observation.

━━━━━━━━━━━━━━

📏 MIDFACE

Observation:
Discuss visible midface proportions.

💡 Why:
Explain what in the photograph supports this.

━━━━━━━━━━━━━━

👄 PHILTRUM

Observation:
Describe the visible philtrum area.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

🗿 MANDIBLE

Observation:
Describe the visible mandibular contour.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

📐 RAMUS

Observation:
Describe the visible ramus area if the photograph allows it.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

📐 GONIAL ANGLE

Observation:
Describe the visible mandibular angle if it can be assessed.

💡 Why:
Explain what is visible.

━━━━━━━━━━━━━━

👤 CHIN / MENTUM

Observation:
Describe chin projection, shape and visible relationship
to the lower face.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

👁️ EYE AREA

Observation:
Describe the visible eye region.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

↗️ CANTHAL TILT

Observation:
Describe the visible orientation of the eye corners.

💡 Why:
Explain whether the photograph actually allows this to be assessed.

━━━━━━━━━━━━━━

👁️ EYE SET

Observation:
Describe visible eye spacing and positioning.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

🧠 BROW RIDGE / BROWS

Observation:
Describe the brow area and visible brow shape.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

👃 NASAL BASE

Observation:
Describe the visible nasal base.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

📏 ALAR WIDTH

Observation:
Describe the visible width of the alar region.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

👃 NASAL PROJECTION

Observation:
Describe visible nasal projection/profile characteristics
only if the angle allows it.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

👄 LIP AREA

Observation:
Describe the visible lip area and proportions.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

💇 HAIRLINE

Observation:
Describe the visible hairline.

💡 Why:
Explain the observation.

━━━━━━━━━━━━━━

💇 HAIR / HAIRSTYLE

Observation:
Describe hairstyle, volume, direction and framing of the face.

💡 Why:
Explain how the hairstyle affects the visual presentation.

━━━━━━━━━━━━━━

🧔 FACIAL HAIR

Observation:
Describe visible facial hair.

💡 Why:
Explain its visual effect on the presentation.

━━━━━━━━━━━━━━

📸 PHOTO / ANGLE ANALYSIS

Lighting:
Describe the lighting.

Camera angle:
Describe the camera position.

Head position:
Describe head tilt/rotation.

Image quality:
Describe sharpness and distortion.

💡 PHOTO LIMITATIONS:
Explain which facial features may be distorted by
camera distance, lens, lighting or head position.

━━━━━━━━━━━━━━

✨ VISUAL PRESENTATION

Describe how hairstyle, lighting, camera angle, grooming
and clothing affect the presentation.

━━━━━━━━━━━━━━

💡 RECOMMENDATIONS

Give practical recommendations ONLY regarding:

• hairstyle
• grooming
• skincare
• clothing
• lighting
• camera distance
• camera angle
• head position
• photography

For every recommendation explain WHY.

━━━━━━━━━━━━━━

🎯 KEY OBSERVATIONS

1.
2.
3.
4.
5.

The key observations must summarize the most noticeable
visible characteristics.

Do not use stars.
Do not use numerical attractiveness ratings.
Do not invent exact measurements.
"""


def analyze_image(image_path, full=False):

    with open(image_path, "rb") as image_file:

        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    if full:

        prompt = FULL_PROMPT

    else:

        prompt = SHORT_PROMPT

    response = client.responses.create(

        model="gpt-5.6-luna",

        input=[
            {
                "role": "user",

                "content": [

                    {
                        "type": "input_text",

                        "text": prompt
                    },

                    {
                        "type": "input_image",

                        "image_url": (
                            f"data:image/jpeg;base64,{image_data}"
                        )
                    }

                ]
            }
        ]
    )

    return response.output_text
