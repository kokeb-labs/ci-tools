// Compliant: every function that initialises a namespace-scope variable is noexcept (Rule 18.4.1).
// Under -fno-exceptions the pack reports them all: the extracted declarations lose noexcept.
#ifndef KV_RULE_18_4_1_OK_NO_EXCEPTIONS_HPP
#define KV_RULE_18_4_1_OK_NO_EXCEPTIONS_HPP

#include <array>
#include <cstdint>

namespace kv::rule_18_4_1::no_exceptions {

struct Config {
  std::uint32_t value{0U};
};

constexpr Config Defaults() noexcept { return Config{.value = 1U}; }

constexpr std::array<std::uint8_t, 4U> MakeTable() noexcept {
  std::array<std::uint8_t, 4U> table{};
  for (std::uint32_t i = 0U; i < 4U; ++i) {
    table[i] = static_cast<std::uint8_t>(i);
  }
  return table;
}

inline constexpr std::array<std::uint8_t, 4U> kTable = MakeTable();
inline constexpr Config kDefaults = Defaults();

inline std::uint32_t DefaultValue() noexcept { return kDefaults.value; }

}  // namespace kv::rule_18_4_1::no_exceptions

#endif  // KV_RULE_18_4_1_OK_NO_EXCEPTIONS_HPP
