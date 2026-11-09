// Seeded violation: std::terminate and std::_Exit.
#include <cstdlib>
#include <exception>

namespace kv::rule_18_5_2::bad_terminate {

void stop(bool now) {
  if (now) {
    std::terminate();
  }
  std::_Exit(2);
}

}  // namespace kv::rule_18_5_2::bad_terminate
