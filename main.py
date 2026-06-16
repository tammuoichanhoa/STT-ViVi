import warnings
from transformers import pipeline

# Suppress a known FutureWarning coming from internal `generation_whisper` (optional)
warnings.filterwarnings(
	"ignore",
	message="The input name `inputs` is deprecated.*",
	category=FutureWarning,
)

# Force CPU usage (device=-1) and load the multilingual Whisper model.
# Pass `language='en'` and `task='translate'` to always translate to English.
transcriber = pipeline(
	"automatic-speech-recognition",
	model="vinai/PhoWhisper-small",
	device=-1,
)

output = transcriber(
	"./samples/sample_000.wav",
	generate_kwargs={"language": "vi"},
)["text"]

print(output)