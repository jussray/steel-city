#include "SteelCityGameState.h"
#include "Net/UnrealNetwork.h"
void ASteelCityGameState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ASteelCityGameState, StarsCollected);
}
bool ASteelCityGameState::AttemptCollectStar(FName Id)
{
    if (!HasAuthority() || !Ledger.TryCollect(Id)) return false;
    StarsCollected = Ledger.Count();
    OnRep_StarsCollected();
    return true;
}
void ASteelCityGameState::OnRep_StarsCollected()
{
    OnStarsChanged.Broadcast(StarsCollected);
}
