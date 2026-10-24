
import { useState } from "react";
import { API_BASE_URL } from "./api";
import "./App.css";

const INTERESTS = [
  "food",
  "culture",
  "photography",
  "music",
  "cooking",
  "art",
  "movies",
  "nature",
  "hiking",
  "sports",
  "games",
  "coffee",
  "history",
  "travel",
  "design",
  "nightlife",
];

const INITIAL_MEMBER = () => ({
  id: crypto.randomUUID(),
  name: "",
  interests: [],
  dislikes: [],
});

function App() {
  const [members, setMembers] = useState([
    { ...INITIAL_MEMBER(), name: "Alex", interests: ["food", "culture"] },
    { ...INITIAL_MEMBER(), name: "Sam", interests: ["music", "cooking"] },
  ]);
  const [location, setLocation] = useState("Bengaluru");
  const [budget, setBudget] = useState("moderate");
  const [occasion, setOccasion] = useState("weekend");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateMember(id, field, value) {
    setMembers((current) =>
      current.map((member) =>
        member.id === id ? { ...member, [field]: value } : member
      )
    );
  }

  function toggleInterest(memberId, field, interest) {
    const member = members.find((item) => item.id === memberId);
    if (!member) return;

    const current = member[field];
    const updated = current.includes(interest)
      ? current.filter((item) => item !== interest)
      : [...current, interest];

    updateMember(memberId, field, updated);
  }

  function addMember() {
    if (members.length < 8) {
      setMembers((current) => [...current, INITIAL_MEMBER()]);
    }
  }

  function removeMember(id) {
    if (members.length > 2) {
      setMembers((current) => current.filter((member) => member.id !== id));
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResults(null);

    const normalizedMembers = members.map((member) => ({
      name: member.name.trim(),
      interests: member.interests,
      dislikes: member.dislikes,
    }));

    if (!location.trim() || location.trim().length < 2) {
      setError("Enter a city or neighbourhood to explore.");
      return;
    }

    if (normalizedMembers.some((member) => !member.name)) {
      setError("Give everyone a name before continuing.");
      return;
    }

    if (normalizedMembers.some((member) => member.interests.length === 0)) {
      setError("Choose at least one interest for every group member.");
      return;
    }

    const names = normalizedMembers.map((member) => member.name.toLowerCase());

    if (new Set(names).size !== names.length) {
      setError("Each group member needs a unique name.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          members: normalizedMembers,
          location: location.trim(),
          budget,
          occasion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail;

        throw new Error(
          detail || "Could not generate recommendations."
        );
      }

      setResults(data);
    } catch (err) {
      setError(
        `${err.message} Check that the CommonGround AI backend is running.`
      );
    } finally {
      setLoading(false);
    }
  }

  const qloo = results?.qloo_discovery;
  const qlooCandidates = Array.isArray(qloo?.candidates)
    ? qloo.candidates
    : [];

  function formatLabel(value) {
    if (!value) return "";
    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (character) => character.toUpperCase());
  }

  return (
    <main className="app">
      <header className="topbar">
        <a className="brand" href="#">
          <span className="brand-mark">c.</span>
          <span>
            commonground<span className="brand-ai"> AI</span>
          </span>
        </a>
        <span className="topbar-note">BETTER TOGETHER, BY DESIGN</span>
      </header>

      <section className="hero">
        <span className="eyebrow">YOUR GROUP. YOUR TASTES. ONE PLAN.</span>
        <h1>
          Different tastes.
          <br />
          <span>Common ground.</span>
        </h1>
        <p className="subtitle">
          Tell us what everyone loves. We'll help you discover experiences
          that bring your group together.
        </p>
      </section>

      <form className="planner" onSubmit={handleSubmit}>
        <div className="section-heading">
          <div>
            <span className="step-label">01 — THE PEOPLE</span>
            <h2>Who's coming?</h2>
            <p>Every great plan starts by understanding everyone.</p>
          </div>
          <span className="count-pill">{members.length} / 8 people</span>
        </div>

        <div className="members">
          {members.map((member, index) => (
            <section className="member-card" key={member.id}>
              <div className="member-heading">
                <span className="member-number">
                  {String(index + 1).padStart(2, "0")} <span aria-hidden="true">·</span>
                </span>
                <input
                  aria-label={`Member ${index + 1} name`}
                  className="name-input"
                  placeholder="Their name"
                  maxLength={40}
                  value={member.name}
                  onChange={(event) =>
                    updateMember(member.id, "name", event.target.value)
                  }
                  required
                />
                {members.length > 2 && (
                  <button
                    type="button"
                    className="remove-button"
                    onClick={() => removeMember(member.id)}
                    aria-label={`Remove ${member.name || "member"}`}
                  >
                    Remove
                  </button>
                )}
              </div>

              <p className="field-label">What are they into?</p>
              <div className="chips">
                {INTERESTS.map((interest) => (
                  <button
                    type="button"
                    key={interest}
                    className={`chip ${
                      member.interests.includes(interest) ? "selected" : ""
                    }`}
                    aria-pressed={member.interests.includes(interest)}
                    onClick={() =>
                      toggleInterest(member.id, "interests", interest)
                    }
                  >
                    {interest}
                  </button>
                ))}
              </div>

              <details className="dislikes-details">
                <summary>Anything they'd rather avoid?</summary>
                <div className="chips dislike-chips">
                  {INTERESTS.map((interest) => (
                    <button
                      type="button"
                      key={interest}
                      className={`chip ${
                        member.dislikes.includes(interest) ? "selected" : ""
                      }`}
                      aria-pressed={member.dislikes.includes(interest)}
                      onClick={() =>
                        toggleInterest(member.id, "dislikes", interest)
                      }
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </details>
            </section>
          ))}
        </div>

        <button
          className="add-member"
          type="button"
          onClick={addMember}
          disabled={members.length >= 8}
        >
          + Add another person
        </button>

        <div className="section-heading preferences-heading">
          <div>
            <span className="step-label">02 — THE PLAN</span>
            <h2>Set the scene.</h2>
            <p>A few details help shape a more relevant recommendation.</p>
          </div>
        </div>

        <div className="preferences-grid">
          <label className="form-field">
            <span>Where are you planning?</span>
            <input
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="City or neighbourhood"
              maxLength={120}
              minLength={2}
              required
            />
          </label>

          <label className="form-field">
            <span>What's the budget?</span>
            <select
              value={budget}
              onChange={(event) => setBudget(event.target.value)}
            >
              <option value="low">Budget-friendly</option>
              <option value="moderate">A little flexibility</option>
              <option value="premium">Premium experience</option>
            </select>
          </label>

          <label className="form-field">
            <span>What's the occasion?</span>
            <select
              value={occasion}
              onChange={(event) => setOccasion(event.target.value)}
            >
              <option value="casual">Just hanging out</option>
              <option value="celebration">A celebration</option>
              <option value="date">A date</option>
              <option value="weekend">Weekend plans</option>
              <option value="team_outing">Team outing</option>
            </select>
          </label>
        </div>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        <button className="submit-button" type="submit" disabled={loading}>
          {loading ? "Finding your common ground..." : "Find our common ground"}
          {!loading && <span aria-hidden="true"> ↗</span>}
        </button>
        <p className="privacy-note">
          Your group preferences are used to generate this request.
        </p>
      </form>

      {results && (
        <>
          <section className="results-section" aria-live="polite">
            <div className="section-heading">
              <div>
                <span className="step-label">03 — THE SHORTLIST</span>
                <h2>Your group, in sync.</h2>
                <p>
                  {results.recommendation_count} ideas ranked for your group in{" "}
                  {results.location}. Each score reflects how well the activity
                  concept matches the group's stated preferences and budget.
                </p>
              </div>
            </div>

            <div className="results-note">
              These are concept recommendations ranked by our local scoring
              engine. They are not verified venues or live availability.
            </div>

            <div className="results-grid">
              {(results.recommendations || []).map((item, index) => (
                <article className="result-card" key={item.category}>
                  <div className="result-card-top">
                    <span className="result-rank">
                      {String(index + 1).padStart(2, "0")} <span aria-hidden="true">·</span>
                    </span>
                    <span className="category-label">{formatLabel(item.category)}</span>
                  </div>

                  <div className="score-row">
                    <span className="score-number">
                      {item.compatibility_score}
                    </span>
                    <span className="score-caption">/ 100 compatibility</span>
                  </div>

                  <div
                    className="score-track"
                    role="progressbar"
                    aria-label={`${item.title} compatibility`}
                    aria-valuenow={item.compatibility_score}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="score-fill"
                      style={{ width: `${item.compatibility_score}%` }}
                    />
                  </div>

                  <h3>{item.title}</h3>
                  <p className="result-explanation">{item.explanation}</p>

                  {item.tradeoffs?.length > 0 && (
                    <details className="tradeoffs">
                      <summary>
                        See trade-offs ({item.tradeoffs.length})
                      </summary>
                      <ul>
                        {item.tradeoffs.map((tradeoff) => (
                          <li key={tradeoff}>{tradeoff}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </article>
              ))}
            </div>

            <p className="engine-note">
              Activity concepts ranked by {formatLabel(results.engine)}.
            </p>
          </section>

          <section className="results-section places-section" aria-live="polite">
            <div className="section-heading">
              <div>
                <span className="step-label">04 — PLACE DISCOVERY</span>
                <h2>Places to explore.</h2>
                <p>
                  Qloo-discovered candidates for {results.location}, based on
                  your group's combined interests.
                </p>
              </div>
              <span className="count-pill">
                {qloo?.status === "available"
                  ? `${qlooCandidates.length} places`
                  : "Qloo discovery"}
              </span>
            </div>

            {qloo?.status === "available" && qlooCandidates.length > 0 ? (
              <>
                <div className="results-note">
                  Qloo supplied these place candidates and their metadata. The
                  interest-match estimate is calculated by CommonGround AI from
                  available names, tags, and metadata; it is not a Qloo
                  compatibility score. Venue suitability, current operating
                  status, prices, and availability have not been verified.
                </div>

                <div className="results-grid">
                  {qlooCandidates.map((place) => (
                    <article
                      className="result-card place-card"
                      key={place.entity_id || place.name}
                    >
                      <div
                        className="place-card-heading"
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "flex-start",
                          gap: "10px",
                          marginBottom: "18px",
                        }}
                      >
                        <span className="result-rank">QLOO PLACE</span>
                        {Number.isFinite(place.interest_relevance_score) && (
                          <span
                            className="category-label place-relevance"
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              maxWidth: "100%",
                              whiteSpace: "normal",
                              lineHeight: 1.5,
                              overflowWrap: "anywhere",
                            }}
                          >
                            Interest match estimate: {place.interest_relevance_score}/100
                          </span>
                        )}
                      </div>

                      <h3
                        className="place-title"
                        style={{ marginBottom: "10px", overflowWrap: "anywhere" }}
                      >
                        {place.name}
                      </h3>

                      {place.address && (
                        <p
                          className="place-address"
                          style={{
                            margin: "0 0 16px",
                            color: "#71796e",
                            fontSize: "12px",
                            lineHeight: 1.7,
                            overflowWrap: "anywhere",
                          }}
                        >
                          {place.address}
                        </p>
                      )}

                      <div
                        className="place-meta"
                        style={{
                          display: "flex",
                          alignItems: "center",
                          flexWrap: "wrap",
                          columnGap: "12px",
                          rowGap: "8px",
                          marginTop: "4px",
                          color: "#586456",
                          fontSize: "12px",
                        }}
                      >
                        {place.business_rating != null &&
                          Number.isFinite(Number(place.business_rating)) && (
                            <span
                              className="place-rating"
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "5px",
                                fontWeight: 700,
                              }}
                            >
                              <span aria-hidden="true">★</span>
                              <span>{Number(place.business_rating).toFixed(1)}</span>
                              <span
                                className="place-meta-label"
                                style={{ color: "#858b7f", fontWeight: 400 }}
                              >
                                rating
                              </span>
                            </span>
                          )}

                        {place.price_level != null && (
                          <span
                            className="place-price"
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "5px",
                              color: "#586456",
                            }}
                          >
                            {place.business_rating != null &&
                              Number.isFinite(Number(place.business_rating)) && (
                                <span aria-hidden="true" style={{ color: "#a0a79b" }}>·</span>
                              )}
                            <span>Price level {place.price_level}</span>
                          </span>
                        )}
                      </div>

                      {place.website && (
                        <a
                          className="place-link"
                          href={place.website}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Visit website <span aria-hidden="true">↗</span>
                        </a>
                      )}
                    </article>
                  ))}
                </div>

                {qloo?.notice && (
                  <p className="engine-note">{qloo.notice}</p>
                )}
              </>
            ) : (
              <div className="results-note">
                {qloo?.notice ||
                  "No place candidates were returned for this request."}
                {qloo?.status === "unavailable" &&
                  " Your local activity recommendations are still available above."}
              </div>
            )}

            {qloo?.resolved_interests?.length > 0 && (
              <p className="engine-note">
                Interests resolved for discovery:{" "}
                {qloo.resolved_interests.join(", ")}.
              </p>
            )}
          </section>
        </>
      )}

      <footer className="site-footer">
        <span className="brand footer-brand">
          <span className="brand-mark">c.</span>
          commonground AI
        </span>
        <p>Better plans begin with understanding each other.</p>
      </footer>
    </main>
  );
}

export default App;
