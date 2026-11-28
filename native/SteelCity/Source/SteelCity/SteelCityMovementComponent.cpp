#include "SteelCityMovementComponent.h"
USteelCityMovementComponent::USteelCityMovementComponent()
{
    MaxWalkSpeed = 600.f;
    MaxFlySpeed = 2000.f;
    JumpZVelocity = 700.f;
    BrakingDecelerationFlying = 1500.f;
}
void USteelCityMovementComponent::ToggleFlight()
{
    if (!HasValidData()) return;
    if (IsFlying())
    {
        SetMovementMode(MOVE_Falling);
    }
    else if (IsMovingOnGround() || IsFalling())
    {
        StopMovementImmediately();
        SetMovementMode(MOVE_Flying);
    }
}
