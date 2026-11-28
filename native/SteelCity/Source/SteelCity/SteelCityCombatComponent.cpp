#include "SteelCityCombatComponent.h"
#include "Engine/World.h"
bool USteelCityCombatComponent::RequestBlast()
{
    const UWorld* World = GetWorld();
    if (!World || !GetOwner() || !GetOwner()->HasAuthority()) return false;
    const double Now = World->GetTimeSeconds();
    if (Now < NextBlastTime) return false;
    NextBlastTime = Now + 0.3;
    OnBlastRequested.Broadcast();
    return true;
}
