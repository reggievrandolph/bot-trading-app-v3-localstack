/**
 * Converts "HH:mm:ss YYYY-MM-DD" to "hh:mm:ss AM/PM YYYY-MM-DD".
 * @param {string} datetime - Example: "18:40:02 2025-05-27"
 * @returns {string} - Example: "6:40:02 PM 2025-05-27"
 */
export function convertTo12Hour(datetime) {
  if (!datetime || typeof datetime !== "string") {
    throw new Error("Invalid datetime input");
  }

  const [timePart, datePart] = datetime.split(" ");
  if (!timePart || !datePart) {
    throw new Error("Invalid datetime format. Expecting 'HH:mm:ss YYYY-MM-DD'");
  }

  const isoString = `${datePart}T${timePart}`;
  const date = new Date(isoString);

  if (isNaN(date.getTime())) {
    throw new Error("Invalid date or time");
  }

  const time = date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });

  return `${time} ${datePart}`;
}
