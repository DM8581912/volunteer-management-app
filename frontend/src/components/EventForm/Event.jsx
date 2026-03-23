import React, { useState } from "react";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import styles from "./Event.module.css";
import Select from "react-select";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const EventSchema = Yup.object().shape({
  eventName: Yup.string()
    .min(5, "Event name must be at least 5 characters")
    .required("Required"),
  eventDescription: Yup.string().required("You must enter a description"),
  location: Yup.string().required("You must enter a location"),
  requiredSkills: Yup.array()
    .min(1, "At least one skill is required")
    .required("Required"),
  urgency: Yup.string().required("Urgency is required"),
  eventDate: Yup.date()
    .min(new Date(), "Event date must be in the future")
    .required("Event date is required"),
});

const skillOptions = [
  { value: "first aid", label: "First Aid" },
  { value: "heavy lifting", label: "Heavy Lifting" },
  { value: "organizing", label: "Organizing" },
  { value: "communication", label: "Communication" },
  { value: "tech", label: "Tech" },
  { value: "leadership", label: "Leadership" },
  { value: "fundraising", label: "Fundraising" },
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

const Event = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFormSubmit = async (values, { resetForm }) => {
    setIsSubmitting(true);
    try {
      const payload = {
        eventName: values.eventName,
        eventDescription: values.eventDescription,
        location: values.location,
        requiredSkills: values.requiredSkills,
        urgency: values.urgency,
        eventDate: values.eventDate.toISOString().split("T")[0],
      };
      console.log("Event submitted:", payload);
      resetForm();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.eventContainer}>
      <h2>Event Management Form</h2>
      <Formik
        initialValues={{
          eventName: "",
          eventDescription: "",
          location: "",
          requiredSkills: [],
          urgency: "",
          eventDate: null,
        }}
        validationSchema={EventSchema}
        onSubmit={handleFormSubmit}
      >
        {({ setFieldValue, values }) => (
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
                value={skillOptions.filter((opt) =>
                  values.requiredSkills.includes(opt.value)
                )}
                onChange={(selected) => {
                  const selectedValues = selected
                    ? selected.map((opt) => opt.value)
                    : [];
                  setFieldValue("requiredSkills", selectedValues);
                }}
                options={skillOptions}
                placeholder="Select skills"
                isMulti
                styles={selectStyles}
              />
              <ErrorMessage
                name="requiredSkills"
                component="div"
                className={styles.error}
              />
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
                selected={values.eventDate}
                onChange={(date) => setFieldValue("eventDate", date)}
                minDate={new Date()}
                placeholderText="Select event date"
              />
              <ErrorMessage
                name="eventDate"
                component="div"
                className={styles.error}
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
