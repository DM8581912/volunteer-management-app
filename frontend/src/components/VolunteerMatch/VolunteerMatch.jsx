import { useState, useEffect } from "react";
import styles from "./VolunteerMatch.module.css";
import { toast } from "react-toastify";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const VolunteerMatch = () => {
  const [selectedVolunteer, setSelectedVolunteer] = useState("");
  const [matchedEvents, setMatchedEvents] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchVolunteers();
  }, []);

  const fetchVolunteers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/eventform`);
      if (!response.ok) return;
      // Volunteers would come from a users endpoint in a full implementation
    } catch (error) {
      toast.error("Failed to load volunteers");
    }
  };

  const handleMatch = async (e) => {
    e.preventDefault();

    if (!selectedVolunteer) {
      toast.error("Please select a volunteer");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/matches/volunteer/${selectedVolunteer}`
      );
      const data = await response.json();

      if (response.ok) {
        setMatchedEvents(data.matches || []);
        if (data.matches?.length === 0) {
          toast.info("No matching events found for this volunteer");
        }
      } else {
        toast.error(data.error || "Failed to find matches");
      }
    } catch (error) {
      toast.error("Unable to connect to server. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.App}>
      <h1>Volunteer Matching Form</h1>

      <form onSubmit={handleMatch} className={styles.form}>
        <label htmlFor="volunteer_id" className={styles.label}>
          Select Volunteer:
        </label>
        <input
          type="text"
          id="volunteer_id"
          value={selectedVolunteer}
          onChange={(e) => setSelectedVolunteer(e.target.value)}
          placeholder="Enter volunteer username"
          className={styles.select}
        />

        <button type="submit" className={styles.button} disabled={isLoading}>
          {isLoading ? "Matching..." : "Match Volunteer"}
        </button>
      </form>

      <div className={styles.matchedEvents}>
        <h2>Matched Events</h2>

        {matchedEvents.length > 0 ? (
          <ul className={styles.eventsList}>
            {matchedEvents.map((match, index) => (
              <li key={index} className={styles.eventItem}>
                {match.event?.eventName} (Location: {match.event?.location}) -
                Match: {Math.round(match.matchScore)}%
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.noEvents}>
            No events matched for the selected volunteer.
          </p>
        )}
      </div>
    </div>
  );
};

export default VolunteerMatch;
