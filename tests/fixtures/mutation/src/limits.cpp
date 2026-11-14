#include "limits.hpp"

namespace fixture {

int Clamp(int value, int low, int high) noexcept {
  if (value < low) {
    return low;
  }
  if (value > high) {
    return high;
  }
  return value;
}

bool Step(int& count) noexcept {
  if (count >= kMax) {
    return false;
  }
  count = count + 1;
  return true;
}

}  // namespace fixture
