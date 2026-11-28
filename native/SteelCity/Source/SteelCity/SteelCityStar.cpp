#include "SteelCityStar.h"
#include "SteelCityHero.h"
#include "SteelCityGameState.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
ASteelCityStar::ASteelCityStar()
{
    bReplicates = true;
    Collision = CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));
    SetRootComponent(Collision);
    Collision->InitSphereRadius(90.f);
    Collision->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Collision->SetCollisionResponseToAllChannels(ECR_Ignore);
    Collision->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(Collision);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void ASteelCityStar::BeginPlay()
{
    Super::BeginPlay();
    if (!HasAuthority()) return;
    if (ASteelCityGameState* State = GetWorld()->GetGameState<ASteelCityGameState>())
    {
        State->OnStarsChanged.AddDynamic(this, &ASteelCityStar::OnStarsChanged);
        OnStarsChanged(State->StarsCollected);
        Collision->OnComponentBeginOverlap.AddDynamic(this, &ASteelCityStar::OnOverlap);
    }
}
void ASteelCityStar::OnOverlap(UPrimitiveComponent*, AActor* Other, UPrimitiveComponent*, int32, bool, const FHitResult&)
{
    if (!HasAuthority() || !Cast<ASteelCityHero>(Other)) return;
    if (ASteelCityGameState* State = GetWorld()->GetGameState<ASteelCityGameState>())
    {
        if (State->AttemptCollectStar(PickupId)) Deactivate();
    }
}
void ASteelCityStar::OnStarsChanged(int32 Count)
{
    if (Count >= FSteelCityStarLedger::Target) Deactivate();
}
void ASteelCityStar::Deactivate()
{
    SetActorHiddenInGame(true);
    SetActorEnableCollision(false);
}
