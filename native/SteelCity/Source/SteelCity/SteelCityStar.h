#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SteelCityStar.generated.h"
class USphereComponent;
class UStaticMeshComponent;
UCLASS()
class STEELCITY_API ASteelCityStar : public AActor
{
    GENERATED_BODY()
public:
    ASteelCityStar();
protected:
    virtual void BeginPlay() override;
    UPROPERTY(EditInstanceOnly, Category="Steel City") FName PickupId;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USphereComponent> Collision;
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Mesh;
    UFUNCTION() void OnOverlap(UPrimitiveComponent* Component, AActor* Other, UPrimitiveComponent* OtherComponent, int32 BodyIndex, bool bFromSweep, const FHitResult& Hit);
    UFUNCTION() void OnStarsChanged(int32 Count);
private:
    void Deactivate();
};
