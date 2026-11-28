#include "SteelCityHero.h"
#include "SteelCityMovementComponent.h"
#include "SteelCityCombatComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/InputComponent.h"
#include "SteelCityInteractable.h"
#include "Engine/World.h"
ASteelCityHero::ASteelCityHero(const FObjectInitializer& Initializer)
    : Super(Initializer.SetDefaultSubobjectClass<USteelCityMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    bUseControllerRotationYaw = false;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 400.f;
    CameraBoom->bUsePawnControlRotation = true;
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    // Local camera-only art direction; no world-volume or replicated-state mutation.
    // Neutral-centered multipliers are starting values, not a calibrated render.
    FollowCamera->PostProcessBlendWeight = 0.65f;
    FPostProcessSettings& Look = FollowCamera->PostProcessSettings;
    Look.bOverride_BloomIntensity = true;
    Look.BloomIntensity = 1.5f;
    Look.bOverride_ColorGammaShadows = true;
    Look.ColorGammaShadows = FVector4(0.95f, 1.0f, 1.08f, 1.0f);
    Look.bOverride_ColorGainHighlights = true;
    Look.ColorGainHighlights = FVector4(1.08f, 1.03f, 0.95f, 1.0f);

    CombatComponent = CreateDefaultSubobject<USteelCityCombatComponent>(TEXT("CombatComponent"));
}
void ASteelCityHero::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindAxis("MoveForward", this, &ASteelCityHero::MoveForward);
    Input->BindAxis("MoveRight", this, &ASteelCityHero::MoveRight);
    Input->BindAxis("MoveVertical", this, &ASteelCityHero::MoveVertical);
    Input->BindAxis("Turn", this, &APawn::AddControllerYawInput);
    Input->BindAxis("LookUp", this, &APawn::AddControllerPitchInput);
    Input->BindAction("Fly", IE_Pressed, this, &ASteelCityHero::ToggleFlight);
    Input->BindAction("Blast", IE_Pressed, this, &ASteelCityHero::Blast);
    Input->BindAction("Talk", IE_Pressed, this, &ASteelCityHero::Talk);
    Input->BindAction("Jump", IE_Pressed, this, &ACharacter::Jump);
    Input->BindAction("Jump", IE_Released, this, &ACharacter::StopJumping);
}
void ASteelCityHero::MoveForward(float Value)
{
    if (!Controller) return;
    const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
    AddMovementInput(Yaw.Vector(), Value);
}
void ASteelCityHero::MoveRight(float Value)
{
    if (!Controller) return;
    const FRotator Yaw(0.f, Controller->GetControlRotation().Yaw, 0.f);
    AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Value);
}
void ASteelCityHero::MoveVertical(float Value)
{
    if (GetCharacterMovement()->IsFlying()) AddMovementInput(FVector::UpVector, Value);
}
void ASteelCityHero::ToggleFlight()
{
    if (USteelCityMovementComponent* Movement = Cast<USteelCityMovementComponent>(GetCharacterMovement())) Movement->ToggleFlight();
}
void ASteelCityHero::Blast()
{
    if (CombatComponent) CombatComponent->RequestBlast();
}

AActor* ASteelCityHero::FindTalkTarget() const
{
    if (!HasAuthority() || !GetWorld() || GetCharacterMovement()->IsFlying()) return nullptr;
    const FVector Start=GetActorLocation();
    const FVector End=Start+GetActorForwardVector()*800.f; // provisional native scale
    FCollisionQueryParams Params(SCENE_QUERY_STAT(SteelCityTalk),false,this);
    FHitResult Hit;
    if (!GetWorld()->LineTraceSingleByChannel(Hit,Start,End,ECC_Visibility,Params)) return nullptr;
    AActor* Target=Hit.GetActor();
    return IsValid(Target) && Target->GetClass()->ImplementsInterface(USteelCityInteractable::StaticClass()) ? Target : nullptr;
}
void ASteelCityHero::Talk()
{
    if (AActor* Target=FindTalkTarget()) LastDialogue=ISteelCityInteractable::Execute_Interact(Target,this);
}
