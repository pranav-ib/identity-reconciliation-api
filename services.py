from supabase_client import supabase

def build_response(group):
    emails = set()
    phoneNumbers = set()
    secondIds = set()
    primaryId = None

    for c in group:
        if c["linkprecedence"] == "primary":
            primaryId = c["id"]

        if c["email"]:
            emails.add(c["email"])

        if c["phonenumber"]:
            phoneNumbers.add(c["phonenumber"])

        if c["linkprecedence"] == "secondary":
            secondIds.add(c["id"])

    return {
        "contact": {
            "primaryContactId": primaryId,
            "emails": list(emails),
            "phoneNumbers": list(phoneNumbers),
            "secondaryContactIds": list(secondIds)
        }
    }
        
def identify_contact(email, phone):

    query = supabase.table("contact").select("*")

    if email and phone:
        query = query.or_(f'email.eq."{email}",phonenumber.eq."{phone}"')
    elif email:
        query = query.eq("email", email)
    else:
        query = query.eq("phonenumber", phone)

    matches = query.execute().data

    if not matches:

        newContact = (
            supabase.table("contact")
            .insert({
                "email":email,
                "phonenumber": phone,
                "linkedid": None,
                "linkprecedence": "primary"
            })
            .execute().data[0]
        )

        return build_response([newContact])
    
    primaryIds = set()
    for contact in matches:
        if contact["linkprecedence"] == "primary":
            primaryIds.add(contact["id"])
        else:
            primaryIds.add(contact["linkedid"])
    
    primaryIds = list(primaryIds)

    primairyContacts = (
        supabase.table("contact")
        .select("*").in_("id", primaryIds)
        .execute().data
    )

    primary = sorted(primairyContacts, key=lambda x: x["createdat"])[0]
    primaryId = primary["id"]

    for p in primairyContacts:
        if p["id"] != primaryId:
            supabase.table("contact").update(
                {
                    "linkedid": primaryId,
                    "linkprecedence": "secondary"
                }
            ).eq("id", p["id"]).execute()

    group = (
        supabase.table("contact")
        .select("*")
        .or_(f"id.eq.{primaryId},linkedid.eq.{primaryId}")
        .order("createdat")
        .execute()
        .data
    )

    ids = [c["id"] for c in group]

    extra = (
        supabase.table("contact")
        .select("*")
        .in_("linkedid", ids)
        .execute()
        .data
    )

    group.extend(extra)

    email_exist = False
    phone_exist = False

    for c in group :
        if email and c["email"] == email:
            email_exist = True
        if phone and c["phonenumber"] == phone:
            phone_exist = True
    
    if not(email_exist and phone_exist):
        newSecondary = (
            supabase.table("contact").insert({
                "email": email,
                "phonenumber": phone,
                "linkedid": primaryId,
                "linkprecedence": "secondary"
            }).execute().data[0]
        )
        group.append(newSecondary)

    return build_response(group)