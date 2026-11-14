// The ru-mutation self-test fixture: a clamp and a bounded counter.
#pragma once

namespace fixture {

constexpr int kMax = 100;

// value limited to [low, high].
int Clamp(int value, int low, int high) noexcept;

// true while count is below kMax; counts up.
bool Step(int& count) noexcept;

}  // namespace fixture
