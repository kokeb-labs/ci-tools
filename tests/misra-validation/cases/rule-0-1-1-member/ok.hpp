// Compliant: writes to data members of *this (an element of a std::array member, and a member
// selected by a pointer to member). They are not objects with automatic storage duration, and
// GetConfig() observes them after the call.
#ifndef KV_RULE_0_1_1_OK_MEMBER_HPP
#define KV_RULE_0_1_1_OK_MEMBER_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_0_1_1::ok_member {

struct Config {
  std::array<std::uint16_t, 4> alarms{};
  std::uint16_t mask{0U};
};

template <typename Port>
class Driver {
 public:
  void SetAlarm(std::size_t i, std::uint16_t v) noexcept {
    if (i < config_.alarms.size()) {
      config_.alarms[i] = v;  // element of a member array
    }
  }
  void SetField(std::uint16_t Config::*field, std::uint16_t v) noexcept {
    config_.*field = v;  // member selected by a pointer to member; field itself is only read
  }
  [[nodiscard]] const Config& GetConfig() const noexcept { return config_; }

 private:
  Config config_{};
};

inline std::uint16_t use() noexcept {
  Driver<int> d{};
  d.SetAlarm(1U, 7U);
  d.SetField(&Config::mask, 3U);
  return (d.GetConfig().mask == 3U) ? d.GetConfig().alarms[1] : std::uint16_t{0U};
}

}  // namespace kv::rule_0_1_1::ok_member

#endif  // KV_RULE_0_1_1_OK_MEMBER_HPP
