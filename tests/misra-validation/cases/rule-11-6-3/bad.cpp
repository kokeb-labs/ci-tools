// Seeded violation: an implicitly valued enumerator gets the same value as an explicit one.
#include <cstdint>

namespace kv::rule_11_6_3::bad {

enum class Code : std::uint8_t { kA = 1, kB, kC = 2 };

bool same(Code x) { return x == Code::kB; }

}  // namespace kv::rule_11_6_3::bad
