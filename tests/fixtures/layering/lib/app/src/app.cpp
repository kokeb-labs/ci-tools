#include "app/app.hpp"

namespace app {

std::uint32_t CountTo(std::uint32_t n) noexcept {
  core::Counter c(n);
  while (c.Increment()) {
  }
  return c.Value();
}

}  // namespace app
