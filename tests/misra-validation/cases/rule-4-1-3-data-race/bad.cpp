// Seeded violation: two threads write one object without synchronisation.
#include <cstdint>
#include <thread>

namespace kv::rule_4_1_3_data_race::bad {

std::uint32_t counter = 0U;

void writer() { counter = 5U; }

void reader() {
  const std::uint32_t seen = counter;
  static_cast<void>(seen);
}

void run() {
  std::thread a(writer);  // writes counter while b reads it, no lock
  std::thread b(reader);
  a.join();
  b.join();
}

}  // namespace kv::rule_4_1_3_data_race::bad
