// Seeded violation: a directive inside the arguments of a macro invocation.
#include <cstdint>

#define KV_PICK(x) (x)

namespace kv::rule_19_3_5::bad {

std::uint32_t pick() {
  return KV_PICK(  // seeded
#ifdef KV_FAST
      1U
#else
      2U
#endif
  );
}

}  // namespace kv::rule_19_3_5::bad
