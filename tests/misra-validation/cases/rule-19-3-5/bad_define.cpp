// Seeded violation: a #define inside the arguments of a macro invocation.
#include <cstdint>

#define KV_ID(x) (x)

namespace kv::rule_19_3_5::bad_define {

std::uint32_t value() {
  return KV_ID(  // seeded
#define KV_INNER 3U
      KV_INNER);
}

}  // namespace kv::rule_19_3_5::bad_define
