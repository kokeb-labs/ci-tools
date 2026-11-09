// Seeded violation: a signal handler installed and a signal raised, with a sig_atomic_t flag.
#include <csignal>

namespace kv::rule_21_10_3::bad {

void on_signal(int number) { static_cast<void>(number); }

int install() {
  std::sig_atomic_t seen = 0;  // seeded: codeql
  static_cast<void>(std::signal(SIGINT, on_signal));  // seeded
  seen = 1;
  return std::raise(SIGINT) + static_cast<int>(seen);  // seeded
}

}  // namespace kv::rule_21_10_3::bad
