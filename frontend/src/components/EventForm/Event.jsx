import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Event.module.css";
import Select from "react-select";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { toast } from "react-toastify";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const EventSchema = Yup.object().shape({
  eventName: Yup.string()
    .min(5, "Event name must be at least 5 characters")
    .required("Required"),
  eventDescription: Yup.string().required("You must enter a description"),
  location: Yup.string().required("You must enter a location"),
  urgency: Yup.string().required("Urgency is required"),
  eventDate: Yup.date().required("Event date is required"),
});

const SKILL_OPTIONS = [
  { value: "Carry over 50 lbs", label: "Carry over 50 lbs" },
  { value: "Run over 20 miles", label: "Run over 20 miles" },
  { value: "First Aid", label: "First Aid" },
  { value: "Communication", label: "Communication" },
  { value: "Leadership", label: "Leadership" },
];

const selectStyles = {
  control: (base) => ({
    ...base,
    height: 40,
    fontSize: 14,
    overflow: "visible",
  }),
  multiValue: (base) => ({
    ...base,
    height: 30,
    overflow: "visible",
  }),
  multiValueLabel: (base) => ({
    ...base,
    overflow: "visible",
  }),
  indicatorSeparator: () => ({ display: "none" }),
};

const INITIAL_VALUES = {
  eventName: "",
  eventDescription: "",
  location: "",
  requiredSkills: [],
  urgency: "",
  eventDate: null,
};

const Event = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [skillsError, setSkillsError] = useState(false);

  const handleFormSubmit = async (values, { resetForm }) => {
    if (selectedSkills.length === 0) {
      setSkillsError(true);
      return;
    }
    setSkillsError(false);

    const eventData = {
      ...values,
      requiredSkills: selectedSkills.map((skill) => skill.value),
      eventDate: selectedDate.toISOString().split("T")[0],
    };

    try {
      const response = await fetch(`${API_BASE_URL}/eventform`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(eventData),
      });

      if (response.ok) {
        toast.success("Event created successfully!");
        resetForm();
        setSelectedSkills([]);
        setSelectedDate(new Date());
      } else {
        const data = await response.json();
        toast.error(data.error || "Failed to create event");
      }
    } catch (error) {
      toast.error("Unable to connect to server. Please try again.");
    }
  };

  return (
    <div className={styles.eventContainer}>
      <h2>Event Management Form</h2>
      <Formik
        initialValues={INITIAL_VALUES}
        validationSchema={EventSchema}
        onSubmit={handleFormSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            <div>
              <label htmlFor="eventName">Event Name</label>
              <Field type="text" name="eventName" />
              <ErrorMessage
                name="eventName"
                component="div"
                className={styles.error}
              />
            </div>
            <div>
              <label htmlFor="eventDescription">Event Description</label>
              <Field as="textarea" name="eventDescription" />
              <ErrorMessage
                name="eventDescription"
                component="div"
                className={styles.error}
              />
            </div>
            <div>
              <label htmlFor="location">Location</label>
              <Field as="textarea" name="location" />
              <ErrorMessage
                name="location"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label>Required Skills</label>
              <Select
                value={selectedSkills}
                onChange={setSelectedSkills}
                options={SKILL_OPTIONS}
                placeholder="Select skills"
                isMulti
                styles={selectStyles}
              />
              {skillsError && (
                <p style={{ color: "red" }}>At least one skill is required</p>
              )}
            </div>

            <div>
              <label htmlFor="urgency">Urgency</label>
              <Field as="select" name="urgency">
                <option value="">Select urgency</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </Field>
              <ErrorMessage
                name="urgency"
                component="div"
                className={styles.error}
              />
            </div>

            <div>
              <label>Event Date</label>
              <DatePicker
                selected={selectedDate}
                onChange={(date) => setSelectedDate(date)}
              />
            </div>

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : "Submit"}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default Event;
