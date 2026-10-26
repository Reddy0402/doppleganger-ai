# Biometric Privacy and Security Architecture

## 1. Ethical Principles and Biometric Notice
Facial images and facial embedding vectors are sensitive biometric-related indicators. Doppelgänger AI is architected under strict privacy-by-design standards:
- **Zero Persistent Selfie Storage**: User-uploaded portraits and camera captures are processed in memory or written to temporary, random UUID-scoped scratch files that are purged immediately upon request completion.
- **Zero Embedding Harvesting**: User query embeddings are never stored in the database or written to gallery indexes unless explicit opt-in consent is provided.
- **Client-Side Export**: The "Share Result Card" generator renders cards strictly within the client browser canvas using image data URLs, ensuring no backend export endpoints expose sensitive user images.
- **No Inappropriate Trait Inferences**: The system explicitly disclaims and prohibits inferences regarding race, ethnicity, medical conditions, sexual orientation, emotional states, criminal propensity, intelligence, or genetic kinship.

## 2. Retention and Cleanup Policy
1. Every upload is assigned a non-deterministic UUIDv4.
2. Temporary files are placed in an isolated temporary directory.
3. Cleanup runs inside Python `try...finally` blocks as well as scheduled background sweeps.
4. An explicit `DELETE /api/uploads/{id}` endpoint allows instant user-triggered deletion of any remaining session traces.

## 3. Gallery Consent and Metadata Governance
All portraits in the gallery must satisfy:
- Author attribution and origin URI.
- Specific license declaration (e.g., CC0, CC-BY, Unsplash License, or explicit participant consent).
- Model and preprocessing version tags to ensure consistent geometric alignment and embedding spaces.
- Immediate removal capability upon request.
