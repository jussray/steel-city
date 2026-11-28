#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SteelCityInteractable.h"
#include "SteelCityNPC.generated.h"
class USphereComponent;
UCLASS()
class STEELCITY_API ASteelCityNPC : public AActor, public ISteelCityInteractable
{
    GENERATED_BODY()
public:
    ASteelCityNPC();
    virtual FText Interact_Implementation(ASteelCityHero* Hero) override;
protected:
    UPROPERTY(VisibleAnywhere) TObjectPtr<USphereComponent> TalkTarget;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FText Dialogue;
};
