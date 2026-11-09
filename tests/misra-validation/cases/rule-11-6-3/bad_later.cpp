// Seeded violation (later): an implicit value equal to an explicit value set before it.
#include <cstdint>

namespace kv::rule_11_6_3::bad_later {

enum class Reg : std::uint8_t { kCtrl = 3, kStat = 2, kData };

bool is_data(Reg r) { return r == Reg::kData; }

}  // namespace kv::rule_11_6_3::bad_later
