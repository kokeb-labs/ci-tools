#include "core/counter.hpp"

/* An example in a comment is not an include:
#include <freertos/FreeRTOS.h>
*/

namespace core {

bool Counter::Increment() noexcept {
  const char* note = "virtual is fine in a string";
  static_cast<void>(note);
  if (value_ >= ceiling_) {
    return false;
  }
  ++value_;
  return true;
}

}  // namespace core
