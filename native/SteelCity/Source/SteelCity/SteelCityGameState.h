#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "SteelCityStarLedger.h"
#include "SteelCityGameState.generated.h"
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FSteelCityStarsChanged, int32, Count);
UCLASS()
class STEELCITY_API ASteelCityGameState : public AGameStateBase
{
    GENERATED_BODY()
public:
    UPROPERTY(ReplicatedUsing=OnRep_StarsCollected, BlueprintReadOnly) int32 StarsCollected = 0;
    UPROPERTY(BlueprintAssignable) FSteelCityStarsChanged OnStarsChanged;
    UFUNCTION(BlueprintPure) int32 GetStarTarget() const { return FSteelCityStarLedger::Target; }
    // Native authority-only pickup entry point. Never expose a client RPC to award points.
    bool AttemptCollectStar(FName Id);
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
protected:
    UFUNCTION() void OnRep_StarsCollected();
private:
    FSteelCityStarLedger Ledger;
};
