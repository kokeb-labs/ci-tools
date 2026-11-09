// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_3_DATA_RACE_OK_NEAR_HPP
#define KV_RULE_4_1_3_DATA_RACE_OK_NEAR_HPP

#include <atomic>
#include <cstdint>
#include <thread>

namespace kv::rule_4_1_3_data_race::near {

// Two threads share a counter only through an atomic.
inline std::uint32_t run() {
  std::atomic<std::uint32_t> counter{0U};
  std::thread writer([&counter]() { counter.store(5U); });
  std::thread reader([&counter]() { static_cast<void>(counter.load()); });
  writer.join();
  reader.join();
  return counter.load();
}

}  // namespace kv::rule_4_1_3_data_race::near

#endif  // KV_RULE_4_1_3_DATA_RACE_OK_NEAR_HPP
