from asyncio.windows_events import NULL


cog_descriptions = {
    "role": "Role Management",
    "faq": "FAQ Functions",
    "feedback": "User Feedback Management",
}


def getDesc(shorthand):

    if cog_descriptions.get(shorthand) != None:
        return cog_descriptions.get(shorthand)
    return shorthand