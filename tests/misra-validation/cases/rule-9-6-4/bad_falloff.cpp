// Seeded violation (falloff): a [[noreturn]] function whose loop can end, so control falls off its end.
#include <cstdint>

namespace kv::rule_9_6_4::bad_falloff {

[[noreturn]] void wait(const volatile bool& ready) {  // seeded
  while (!ready) {
  }
}

}  // namespace kv::rule_9_6_4::bad_falloff
