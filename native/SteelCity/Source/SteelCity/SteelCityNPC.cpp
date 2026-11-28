#include "SteelCityNPC.h"
#include "SteelCityHero.h"
#include "Components/SphereComponent.h"
ASteelCityNPC::ASteelCityNPC()
{
    TalkTarget=CreateDefaultSubobject<USphereComponent>(TEXT("TalkTarget"));
    SetRootComponent(TalkTarget);
    TalkTarget->InitSphereRadius(65.f);
    TalkTarget->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    TalkTarget->SetCollisionResponseToAllChannels(ECR_Ignore);
    TalkTarget->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
}
FText ASteelCityNPC::Interact_Implementation(ASteelCityHero* Hero)
{
    return HasAuthority() && IsValid(Hero) ? Dialogue : FText::GetEmpty();
}
