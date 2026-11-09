// Seeded violation: a function declared [[noreturn]] that can return.
#include <cstdint>

namespace kv::rule_9_6_4::bad {

[[noreturn]] void halt(std::int32_t code) {  // seeded
  if (code == 0) {
    return;
  }
  for (;;) {
  }
}

}  // namespace kv::rule_9_6_4::bad
