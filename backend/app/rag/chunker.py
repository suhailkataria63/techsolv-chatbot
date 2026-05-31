from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_transcript(transcript: str) -> list[str]:
    if not transcript.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
    )
    return splitter.split_text(transcript)
