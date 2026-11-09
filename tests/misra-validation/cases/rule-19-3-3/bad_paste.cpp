// Seeded violation: a parameter used plainly and with ##, given a macro argument.
#include <cstdint>

#define KV_BANK 2U
#define KV_REG(x) (x + kv::rule_19_3_3::bad_paste::k##x)  // seeded

namespace kv::rule_19_3_3::bad_paste {

constexpr std::uint32_t kKV_BANK = 1U;

std::uint32_t reg() { return KV_REG(KV_BANK); }

}  // namespace kv::rule_19_3_3::bad_paste
