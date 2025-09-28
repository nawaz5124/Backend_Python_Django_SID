# api/utils/formatters.py

def format_diff_for_payload(existing, incoming):
    """
    Compare two dictionaries and return a clean formatted diff string.
    Useful for logging changes in personalDetails and addressDetails.
    """
    sections = []

    for section_label, keys in {
        "PERSONAL DETAILS": [
            ("first_name", "firstName"),
            ("last_name", "lastName"),
            ("email", "email"),
            ("mobile", "mobile"),
            ("title", "title"),
            ("org_name", "orgName"),
        ],
        "ADDRESS DETAILS": [
            ("first_line", "firstLine"),
            ("street", "street"),
            ("city", "city"),
            ("county", "county"),
            ("postcode", "postcode"),
        ],
    }.items():
        lines = []
        for model_key, incoming_key in keys:
            old_val = existing.get(model_key)
            new_val = incoming.get(incoming_key)

            if old_val != new_val:
                lines.append(
                    f"- {model_key.replace('_', ' ').title()}: Existing: {old_val or '❌'} | New: {new_val or '❌'}"
                )

        if lines:
            sections.append(f"{section_label}:\n" + "\n".join(lines))

    return "\n\n".join(sections) if sections else None