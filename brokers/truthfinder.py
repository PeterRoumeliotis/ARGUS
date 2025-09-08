from models import ClientProfile, BrokerResult

def search(profile: ClientProfile) -> BrokerResult:
    return BrokerResult(
        broker="TruthFinder",
        found=False,
        notes="Manual check recommended. Opt-out: https://www.truthfinder.com/opt-out/"
    )