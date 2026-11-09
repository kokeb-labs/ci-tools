// Edge cases: more declarations in the global namespace.
#include <cstdint>

enum class KvRule603Mode : std::uint8_t { kIdle, kRun };
using KvRule603Raw = std::uint32_t;
KvRule603Raw kv_rule_6_0_3_mode_raw(KvRule603Mode m) { return static_cast<KvRule603Raw>(m); }
