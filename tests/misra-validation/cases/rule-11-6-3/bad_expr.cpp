// Seeded violation (expr): an explicit value computed from another enumerator duplicates an implicit value.
#include <cstdint>

namespace kv::rule_11_6_3::bad_expr {

enum class Reg : std::uint8_t {
  kA = 3,
  kB,
  kC,  // seeded
  kD = kB + 1
};

bool is_c(Reg r) { return r == Reg::kC; }

}  // namespace kv::rule_11_6_3::bad_expr
